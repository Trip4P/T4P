import math
import json
import re
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
import requests
import sys
import os

# 현재 파일 기준 AI 폴더 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import models
from config import settings
from schemas import BudgetRequest

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# pricelevel → 식사비 매핑 (평균 1인당)
price_map = {
    0: 0,
    1: 7000,
    2: 14000,
    3: 23000,
    4: 40000
}

# 숙박비 계산 함수
def calculate_accommodation_cost(accommodation_price: int, nights: int, num_people: int) -> int:
    if num_people <= 2:
        total_cost = accommodation_price * nights
    else:
        extra_people = num_people - 2
        extra_fee_per_night = accommodation_price * 0.3 * extra_people
        total_cost = (accommodation_price + extra_fee_per_night) * nights
    return int(total_cost)

# 거리 계산 (haversine)
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 교통요금 계산 로직
def calculate_fare_between(loc1, loc2, num_people):
    lat1, lon1 = getattr(loc1, "latitude", None), getattr(loc1, "longitude", None)
    lat2, lon2 = getattr(loc2, "latitude", None), getattr(loc2, "longitude", None)
    if None in (lat1, lon1, lat2, lon2):
        return 0

    dist = haversine(lat1, lon1, lat2, lon2)
    if dist < 2.0:
        return 0

    fare = get_public_transport_fare(lat1, lon1, lat2, lon2)
    if fare == 0:
        if dist < 5:
            fare = 1450
        elif dist < 15:
            fare = 1850
        else:
            fare = 2250

    return fare * num_people

# ODSAY API 호출 (실패시 0 반환)
def get_public_transport_fare(lat1, lon1, lat2, lon2):
    api_key = settings.ODSAY_API_KEY
    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": api_key,
        "SX": lon1,
        "SY": lat1,
        "EX": lon2,
        "EY": lat2,
        "OPT": 0
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return 0
        data = response.json()
        if "result" not in data or "path" not in data["result"] or not data["result"]["path"]:
            return 0
        fare = data["result"]["path"][0]["info"].get("payment")
        return fare if fare else 0
    except:
        return 0

# 교통비 전체 계산
def calculate_transport_cost(plan_data, num_people: int = 1) -> int:
    total_cost = 0
    previous_day_last_place = None

    for day_plan in plan_data.plans:
        schedule = day_plan.schedule

        if previous_day_last_place:
            first_place = schedule[0]
            fare = calculate_fare_between(previous_day_last_place, first_place, num_people)
            total_cost += fare

        for i in range(len(schedule) - 1):
            loc1, loc2 = schedule[i], schedule[i + 1]
            fare = calculate_fare_between(loc1, loc2, num_people)
            total_cost += fare

        previous_day_last_place = schedule[-1]

    return total_cost

# 식사비 계산
def calculate_food_cost(plan_data, num_people: int = 1) -> int:
    total_cost = 0
    for day_plan in plan_data.plans:
        for item in day_plan.schedule:
            price_level = getattr(item, "pricelevel", 0)
            avg_price = price_map.get(price_level, 0)
            total_cost += avg_price * num_people
    return total_cost

# GPT 응답 파싱 → 숫자만 추출 + 무료 처리
def parse_fee(response_text: str) -> int:
    response_text = response_text.strip()
    
    if '무료' in response_text:
        return 0
    
    match = re.search(r'\d+', response_text)
    return int(match.group()) if match else 0

def ask_gpt_for_entry_fee(place_name: str) -> int:
    short_name = place_name[:50]
    prompt = (
    f"'{short_name}'은 한국의 관광지 또는 체험형 시설입니다. "
    f"이 시설은 일반적으로 입장료나 체험비용이 발생할 수 있습니다. "
    f"해당 장소의 평균 입장료 또는 체험비용을 1인당 기준으로 한국 원화로 알려주세요. "
    f"가능하면 최근 2024년~2025년 한국 기준 가격을 참고해 추정해줘. "
    f"만약 입장료가 없거나 무료 시설이라면 반드시 '0'으로 응답해줘. "
    f"반드시 숫자만 단위 없이 정수 형태로 응답해줘. "
    f"예: 15000"
)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.3,
        )
        response_text = response.choices[0].message.content.strip()
        print(f"[GPT 입장료 추정] {place_name} → GPT 응답: {response_text}")
        fee = parse_fee(response_text)
    except Exception as e:
        print(f"입장료 추출 실패: {e}")
        fee = 0
    return fee


def estimate_entry_fees(plan_data, num_people: int = 1) -> int:
    total_fee = 0
    for day_plan in plan_data.plans:
        schedule = day_plan.schedule
        
        
        for item in schedule[:-1]: #마지막 장소가 숙소라는 가정하에 숙소 제외 계산
            place_name = getattr(item, "place", None)
            pricelevel = getattr(item, "pricelevel", 0)
            if pricelevel == 0 and place_name:
                fee = ask_gpt_for_entry_fee(place_name)
                total_fee += fee * num_people
    return total_fee

# GPT 예산 감성 코멘트
def ask_gpt_budget_comment(user_budget: int, end_city: str, days: int = 2, num_people: int = 1) -> str:
    prompt = f"""
{end_city} 지역을 {days}일 동안 {num_people}명이 여행하는 일정이에요.
추천된 여행 코스를 기준으로 예상 여행 비용은 총 {user_budget}원이에요.
너는 최고의 여행 가이드이자 여행 예산 평가 도우미야.
이 금액이 해당 지역(예: 서울시가 아닌 {end_city} 같은 행정구 기준)의 평균 여행 비용과 비교해서
비싸 보이는지, 적당한지, 저렴해 보이는지를 짧게 감성적으로 평가해줘. 그 해당 지역의 평균 여행 비용도 언급해줘.

- "~같아요", "~일 것 같아요", "~하면 좋겠어요"처럼 부드러운 말투로.
- MZ세대 감성 이모지를 센스 있게 활용해줘.
- 설명하지 말고, 친구에게 말하듯 자연스럽고 공감되는 한두 문장으로만 말해줘.
예: "살짝 비싸지만 그만한 가치가 있을 것 같아요 ✨", "가성비 최고 코스예요! 😎👍"
- 비용 느낌뿐 아니라, '왜 그렇게 느껴질 수 있는지'를 센스 있게 살짝 덧붙여줘.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 센스 있는 감성 여행 가이드야. 감성적인 코멘트를 친구에게 말하듯 써줘."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT 예산 코멘트 생성 실패:", e)
        return "예산 분석에 실패했어요. 다음에 다시 시도해 주세요."

# 전체 예산 계산
def calculate_total_budget_from_plan(db: Session, plan_data: BudgetRequest) -> Dict:
    num_people = plan_data.peopleCount

    food_cost = calculate_food_cost(plan_data, num_people)
    entry_fees = estimate_entry_fees(plan_data, num_people)
    transport_cost = calculate_transport_cost(plan_data, num_people)

    # 숙박비 계산
    first_day_schedule = plan_data.plans[0].schedule
    last_item = first_day_schedule[-1]
    accommodation_place_id = getattr(last_item, "placeId", None)

    accommodation_price = 0
    if accommodation_place_id:
        accommodation = db.query(models.Accommodation).filter(
            models.Accommodation.place_id == accommodation_place_id
        ).first()
        if accommodation:
            accommodation_price = accommodation.price

    nights = max(len(plan_data.plans) - 1, 0)
    accommodation_cost = calculate_accommodation_cost(accommodation_price, nights, num_people)

    total_cost = food_cost + entry_fees + transport_cost + accommodation_cost

    end_city = plan_data.endCity if hasattr(plan_data, "endCity") and plan_data.endCity else "여행지"

    budget_comment = ask_gpt_budget_comment(
        user_budget=total_cost,
        end_city=end_city,
        days=len(plan_data.plans),
        num_people=num_people
    )

    return {
        "food_cost": food_cost,
        "entry_fees": entry_fees,
        "transport_cost": transport_cost,
        "accommodation_cost": accommodation_cost,
        "total_cost": total_cost,
        "comment": budget_comment
    }

if __name__ == "__main__":
    print("포스트맨에서 받은 데이터를 calculate_total_budget_from_plan(plan_data)로 넘겨주세요.")
