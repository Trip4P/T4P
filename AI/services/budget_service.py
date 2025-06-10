import math
import json
import re
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
import requests
import sys
from functools import lru_cache
import aiohttp
import asyncio

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

def get_place_price_info(db: Session, place_id: str) -> Dict:
    """
    place_id 기준으로 Meals, Accommodations, Destinations 테이블에서 pricelevel이나 price 조회
    """
    # Meals 조회 (식사)
    meal = db.query(models.Meal).filter(models.Meal.place_id == place_id).first()
    if meal:
        return {
            "type": "meal",
            "pricelevel": meal.price_level,  # 주의: price_level 컬럼명
            "price": None
        }

    # Accommodations 조회 (숙박)
    accommodation = db.query(models.Accommodation).filter(models.Accommodation.place_id == place_id).first()
    if accommodation:
        return {
            "type": "accommodation",
            "pricelevel": None,
            "price": accommodation.price
        }

    # Destinations 조회 (관광지)
    destination = db.query(models.Destination).filter(models.Destination.place_id == place_id).first()
    if destination:
        return {
            "type": "destination",
            "pricelevel": destination.price_level,
            "price": None
        }

    # 못 찾았을 때
    return {
        "type": "unknown",
        "pricelevel": None,
        "price": None
    }


def calculate_accommodation_cost(db: Session, plan_data, num_people: int = 1) -> int:
    total_cost = 0

    # 마지막 날 제외하고 숙소 계산
    for day_plan in plan_data.plans[:-1]:
        schedule = day_plan.schedule
        if not schedule:
            continue  # 일정이 비어있는 경우 방어

        last_place = schedule[-1]
        place_id  = last_place.placeId
        place_info = get_place_price_info(db, place_id)

        if place_info["type"] == "accommodation" and place_info["price"] is not None:
            price = place_info["price"]
            if num_people <= 2:
                day_cost = price
            else:
                extra_people = num_people - 2
                extra_fee = price * 0.3 * extra_people
                day_cost = price + extra_fee

            total_cost += int(day_cost)

    return total_cost


# 거리 계산 (haversine)
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 교통요금 계산 로직
async def calculate_fare_between(loc1, loc2, num_people):
    lat1, lon1 = getattr(loc1, "latitude", None), getattr(loc1, "longitude", None)
    lat2, lon2 = getattr(loc2, "latitude", None), getattr(loc2, "longitude", None)
    if None in (lat1, lon1, lat2, lon2):
        return 0

    dist = haversine(lat1, lon1, lat2, lon2)
    if dist < 2.0:
        return 0

    fare = await async_get_public_transport_fare(lat1, lon1, lat2, lon2)
    if fare == 0:
        if dist < 5:
            fare = 1450
        elif dist < 15:
            fare = 1850
        else:
            fare = 2250

    return fare * num_people


# ODSAY API 호출 (실패시 0 반환)
odsay_cache = {}

async def async_get_public_transport_fare(lat1, lon1, lat2, lon2):
    key = f"{lat1:.5f}-{lon1:.5f}-{lat2:.5f}-{lon2:.5f}"
    if key in odsay_cache:
        return odsay_cache[key]

    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": settings.ODSAY_API_KEY,
        "SX": lon1,
        "SY": lat1,
        "EX": lon2,
        "EY": lat2,
        "OPT": 0
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                fare = data["result"]["path"][0]["info"].get("payment", 0)
                odsay_cache[key] = fare
                return fare
    except:
        return 0


# 교통비 전체 계산
async def calculate_transport_cost(plan_data, num_people: int = 1) -> int:
    tasks = []

    for i, day_plan in enumerate(plan_data.plans):
        schedule = day_plan.schedule
        if not schedule:
            continue

        # 하루 시작 이동 (전날 → 오늘 첫 장소)
        if i > 0:
            prev_schedule = plan_data.plans[i - 1].schedule
            if prev_schedule:
                tasks.append(calculate_fare_between(prev_schedule[-1], schedule[0], num_people))

        # 당일 내 이동
        for j in range(len(schedule) - 1):
            loc1, loc2 = schedule[j], schedule[j + 1]
            tasks.append(calculate_fare_between(loc1, loc2, num_people))

    fares = await asyncio.gather(*tasks)
    return sum(fares)



# 식사비 계산
def calculate_food_cost(db: Session, plan_data, num_people: int = 1) -> int:
    total_cost = 0
    for day_plan in plan_data.plans:
        for item in day_plan.schedule:
            place_id = item.placeId
            place_info = get_place_price_info(db, place_id)
            if place_info["type"] == "meal":
                pricelevel = place_info["pricelevel"]
                avg_price = price_map.get(pricelevel, 0)
                total_cost += avg_price * num_people
    return total_cost

async def async_ask_gpt_for_entry_fee(place_name: str) -> int:
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
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10,
        "temperature": 0.3
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data) as resp:
                result = await resp.json()
                content = result["choices"][0]["message"]["content"]
                return int(re.search(r'\d+', content).group()) if content else 0
    except Exception as e:
        print(f"[GPT 오류] {place_name}: {e}")
        return 0

async def estimate_entry_fees(db: Session, plan_data, num_people: int = 1) -> int:
    total_fee = 0
    visited_place_ids = set()
    tasks = []
    people_counts = []
    
    for day_plan in plan_data.plans:
        schedule = day_plan.schedule
        for item in schedule[:-1]:  # 마지막은 숙소일 가능성 높으므로 제외
            place_id = item.placeId
            place_name = item.place

            if place_id in visited_place_ids:
                continue
            visited_place_ids.add(place_id)

            place_info = get_place_price_info(db, place_id)

            if place_info["type"] == "destination":
                pricelevel = place_info["pricelevel"]
                if pricelevel is None and place_name:
                    tasks.append(async_ask_gpt_for_entry_fee(place_name))
                    people_counts.append(num_people)
                elif pricelevel and pricelevel > 0:
                    avg_price = price_map.get(pricelevel, 0)
                    total_fee += avg_price * num_people

    if tasks:
        results = await asyncio.gather(*tasks)
        for fee, count in zip(results, people_counts):
            total_fee += fee * count

    return total_fee


# GPT 예산 감성 코멘트
def ask_gpt_budget_comment(user_budget: int, end_city: str, days: int = 2, num_people: int = 1) -> str:
    prompt = f"""
{end_city} 지역을 {days}일 동안 {num_people}명이 여행하는 일정이에요.
추천된 여행 코스를 기준으로 예상 여행 비용은 총 {user_budget}원이에요.
너는 최고의 여행 가이드이자 여행 예산 평가 도우미야.
이 금액이 해당 지역(예: 서울시가 아닌 {end_city} 같은 행정구 기준)의 평균 여행 비용과 비교해서
비싸 보이는지, 적당한지, 저렴해 보이는지를 짧게 감성적으로 평가해줘. 그 해당 지역의 평균 여행 비용도 숫자 금액으로 함께 언급해줘.

- "~같아요", "~일 것 같아요", "~하면 좋겠어요"처럼 부드러운 말투로.
- MZ세대 감성 이모지를 센스 있게 활용해줘.
- 설명하지 말고, 친구에게 말하듯 자연스럽고 공감되는 한두 문장으로만 말해줘.
예: "살짝 비싸지만 그만한 가치가 있을 것 같아요 ✨", "가성비 최고 코스예요! 😎👍"
- 비용 느낌뿐 아니라, '왜 그렇게 느껴질 수 있는지'를 센스 있게 살짝 덧붙여줘.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
async def calculate_total_budget_from_plan(db: Session, plan_data: BudgetRequest) -> Dict:
    num_people = plan_data.peopleCount

    # 동기 함수 그대로 호출
    food_cost = calculate_food_cost(db, plan_data, num_people)
    transport_cost = await calculate_transport_cost(plan_data, num_people)
    accommodation_cost = calculate_accommodation_cost(db, plan_data, num_people)

    # 비동기 함수 호출
    entry_fees = await estimate_entry_fees(db, plan_data, num_people)

    total_cost = food_cost + entry_fees + transport_cost + accommodation_cost

    end_city = getattr(plan_data, "endCity", "여행지")

    # 감성 코멘트는 여전히 동기로 처리
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
