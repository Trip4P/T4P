import math
import json
from typing import List, Dict
import math
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

from models import Budget

# 설정값
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

price_map = {
    0: 0,
    1: 7000,
    2: 14000,
    3: 23000,
    4: 40000
}


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
    print(f"[ODsay API 요청] 출발:({lat1},{lon1}) 도착:({lat2},{lon2})")
    response = requests.get(url, params=params)
    print(f"[ODsay API 응답 코드] {response.status_code}")

    if response.status_code != 200:
        print(f"API 요청 실패: {response.status_code}")
        return 0

    data = response.json()
    # print(f"[ODsay API 응답 데이터] {json.dumps(data, ensure_ascii=False)}")

    if "result" not in data or "path" not in data["result"] or not data["result"]["path"]:
        print("경로 정보 없음")
        return 0

    fare = data["result"]["path"][0]["info"].get("payment")
    if fare is None:
        print("ODsay API 응답에 'payment' 정보가 없습니다.")
        return 0
    print(f"[계산된 요금] {fare}원")
    return fare

def calculate_transport_cost(plan_data, num_people: int = 1) -> int:
    total_cost = 0
    for day_plan in plan_data.plans:  # 딕셔너리 인덱싱 대신 속성 접근
        schedule = day_plan.schedule  # 마찬가지로 속성 접근
        for i in range(len(schedule) - 1):
            loc1 = schedule[i]
            loc2 = schedule[i + 1]
            lat1, lon1 = getattr(loc1, "latitude", None), getattr(loc1, "longitude", None)
            lat2, lon2 = getattr(loc2, "latitude", None), getattr(loc2, "longitude", None)
            if None in (lat1, lon1, lat2, lon2):
                continue

            dist = haversine(lat1, lon1, lat2, lon2)
            if dist < 1.0:
                continue

            fare = get_public_transport_fare(lat1, lon1, lat2, lon2)
            if fare == 0:
                if dist < 3:
                    fare = 1250
                elif dist < 10:
                    fare = 1800
                else:
                    fare = 2500
                print(f"[기본요금 적용] 거리: {dist:.2f}km, 요금: {fare}원")
            else:
                print(f"[API요금] 거리: {dist:.2f}km, 요금: {fare}원")

            total_cost += fare * num_people
    return total_cost



def calculate_food_cost(plan_data: Dict, num_people: int = 1) -> int:
    total_cost = 0
    print("=== calculate_food_cost 시작 ===")
    for day_index, day_plan in enumerate(plan_data.plans, start=1):
        print(f"Day {day_index} 일정:")
        for item in day_plan.schedule:
            # item은 SchedulePlace 객체라고 가정
            price_level = getattr(item, "pricelevel", 0)  # 또는 item.pricelevel
            avg_price = price_map.get(price_level, 0)
            place_name = getattr(item, "place", "N/A")  # 또는 item.place
            print(f"  장소: {place_name} (pricelevel: {price_level}), 비용: {avg_price * num_people}")
            total_cost += avg_price * num_people

    print(f"총 식비: {total_cost}")
    print("=== calculate_food_cost 끝 ===")
    return total_cost


def ask_gpt_for_entry_fee(place_name: str) -> int:
    short_name = place_name[:20]
    prompt = f"'{short_name}'의 평균 입장료(또는 체험 비용)를 한국 원화로 알려줘. 숫자만 단위 없이 정수 형태로 응답해줘. 예: 15000"
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
        fee = int(response_text)
    except Exception as e:
        print(f"입장료 추출 실패: {e}")
        fee = 0
    return fee


def estimate_entry_fees(plan_data: Dict, num_people: int = 1) -> int:
    total_fee = 0
    for day_plan in plan_data.plans:
        for item in day_plan.schedule:  # 딕셔너리 접근 대신 속성 접근
            place_name = getattr(item, "place", None)
            pricelevel = getattr(item, "pricelevel", 0)

            if pricelevel == 0 and place_name:
                print(f"[GPT 요청] '{place_name}'의 입장료 추정 중...")
                fee = ask_gpt_for_entry_fee(place_name)
                print(f"[결과] '{place_name}' 예상 입장료: {fee}원")
                total_fee += fee * num_people
            else:
                print(f"[스킵] '{place_name}'은 pricelevel {pricelevel} 이므로 GPT 요청 안함.")
    return total_fee

# 정류장 못찾을시 거리로 임의 요금 계산
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def ask_gpt_budget_comment(user_budget: int, region_names: List[str], days: int = 2, num_people: int = 1) -> str:
    region_str = ", ".join(region_names)
    prompt = f"""
{region_str} 지역을 {days}일 동안 {num_people}명이 여행하는 일정이에요.
추천된 여행 코스를 기준으로 예상 여행 비용은 총 {user_budget}원이에요.

이 금액이 해당 지역(예: 서울시가 아닌 {region_str} 같은 행정구 기준)의 평균 여행 비용과 비교해서
비싸 보이는지, 적당한지, 저렴해 보이는지를 짧게 감성적으로 평가해줘. 그 해당 지역의 평균 여행 비용도 언급해줘.

👉 "~같아요", "~일 것 같아요", "~하면 좋겠어요"처럼 부드러운 말투로.
👉 MZ세대 감성 이모지를 센스 있게 활용해줘.
👉 설명하지 말고, 친구에게 말하듯 자연스럽고 공감되는 한두 문장으로만 말해줘.
예: "살짝 비싸지만 그만한 가치가 있을 것 같아요 ✨", "가성비 최고 코스예요! 😎👍"
👉 비용 느낌뿐 아니라, '왜 그렇게 느껴질 수 있는지'를 센스 있게 살짝 덧붙여줘.
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


def calculate_total_budget_from_plan(db: Session, plan_data) -> Dict:
    num_people = plan_data.peopleCount

    food_cost = calculate_food_cost(plan_data, num_people)
    entry_fees = estimate_entry_fees(plan_data, num_people)
    transport_cost = calculate_transport_cost(plan_data, num_people)
    total_cost = food_cost + entry_fees + transport_cost

    region_names = []
    seen = set()
    for day_plan in plan_data.plans:
        for item in day_plan.schedule:
            place_id = item.placeId
            if not place_id:
                continue
            place_id_str = str(place_id)
            place = (
                db.query(models.Destination).filter(models.Destination.place_id == place_id_str).first()
                or db.query(models.Meal).filter(models.Meal.place_id == place_id_str).first()
            )
            if place:
                area = getattr(place, "area", None)
                if area and area not in seen:
                    region_names.append(area)
                    seen.add(area)

    budget_comment = ask_gpt_budget_comment(
        total_cost,
        region_names,
        days=len(plan_data.plans),
        num_people=num_people
    )

    budget_data = {
        "food_cost": food_cost,
        "entry_fees": entry_fees,
        "transport_cost": transport_cost,
        "total_cost": total_cost,
        "comment": budget_comment
    }


    return budget_data



if __name__ == "__main__":
    print("포스트맨에서 받은 데이터를 calculate_total_budget_from_plan(plan_data)로 넘겨주세요.")
