import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings

from typing import List, Dict
import math
import json
from sqlalchemy.orm import Session
from openai import OpenAI
import models
from models import Schedule, Budget
from datetime import datetime
import requests

def save_budget(db: Session, schedule_id: int, budget_data: dict):
    new_budget = Budget(
        schedule_id=schedule_id,
        food_cost=budget_data["food_cost"],
        transport_cost=budget_data["transport_cost"],
        entry_fees=budget_data["entry_fees"],
        total_budget=budget_data["total_cost"],
        comment=budget_data.get("comment", ""),
        created_at=datetime.utcnow()
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget

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
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"API 요청 실패: {response.status_code}")
        return 0

    data = response.json()
    if "result" not in data or "path" not in data["result"] or not data["result"]["path"]:
        print("경로 정보 없음")
        print("API 응답 전체:", data)
        return 0

    fare = data["result"]["path"][0]["info"].get("payment")
    if fare is None:
        print("ODsay API 응답에 'payment' 정보가 없습니다.")
        return 0
    return fare

client = OpenAI(api_key=settings.OPENAI_API_KEY)

price_map = {
    0: 0,
    1: 7000,
    2: 14000,
    3: 23000,
    4: 40000
}

def calculate_food_cost(db: Session, plan_json: dict, num_people: int = 1) -> int:
    total_cost = 0
    for day in plan_json.values():
        for meal_type in ["lunch", "dinner"]:
            for meal in day.get(meal_type, []):
                db_meal = db.query(models.Meal).filter(models.Meal.place_id == meal['place_id']).first()
                if db_meal:
                    avg_price = price_map.get(db_meal.price_level, 0)
                    total_cost += avg_price * num_people
    return total_cost

def ask_gpt_for_entry_fee(place_name: str) -> int:
    # 장소명 길이가 너무 길면 핵심 단어만 추출 (예시: 앞 20자만)
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
        print(f"GPT 응답: {response_text}")
        fee = int(response_text)
    except Exception as e:
        print(f"입장료 추출 실패: {e}")
        fee = 0
    return fee


def estimate_entry_fees(db: Session, plan_json: dict, num_people: int = 1) -> int:
    total_fee = 0
    for day in plan_json.values():
        for sight in day.get("sights", []):
            destination = db.query(models.Destination).filter(models.Destination.place_id == sight['place_id']).first()
            if destination:
                fee = ask_gpt_for_entry_fee(destination.name)
                total_fee += fee * num_people
    return total_fee



def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_place_location(db: Session, place_id: str):
    destination = db.query(models.Destination).filter(models.Destination.place_id == place_id).first()
    if destination:
        return destination.latitude, destination.longitude
    meal = db.query(models.Meal).filter(models.Meal.place_id == place_id).first()
    if meal:
        return meal.latitude, meal.longitude
    return None, None

def calculate_transport_cost(db: Session, plan_json: dict, num_people: int = 1) -> int:
    total_cost = 0
    for day in plan_json.values():
        sights = day.get("sights", [])
        lunch = day.get("lunch", [])
        dinner = day.get("dinner", [])

        if len(sights) >= 2 and lunch and dinner:
            s1, s2 = sights[0], sights[1]
            l, d = lunch[0], dinner[0]

            def fare_between(pid1, pid2):
                lat1, lon1 = get_place_location(db, pid1)
                lat2, lon2 = get_place_location(db, pid2)
                if None in (lat1, lon1, lat2, lon2):
                    return 0
                dist = haversine(lat1, lon1, lat2, lon2)
                if dist < 1.0:
                    return 0
                fare = get_public_transport_fare(lat1, lon1, lat2, lon2)
                if fare == 0:
                    if dist < 3:
                        fare = 1250
                    elif dist < 10:
                        fare = 1800
                    else:
                        fare = 2500
                return fare

            route1 = fare_between(s1["place_id"], l["place_id"]) + \
                     fare_between(l["place_id"], s2["place_id"]) + \
                     fare_between(s2["place_id"], d["place_id"])

            route2 = fare_between(s2["place_id"], l["place_id"]) + \
                     fare_between(l["place_id"], s1["place_id"]) + \
                     fare_between(s1["place_id"], d["place_id"])

            average_fare = (route1 + route2) // 2
            total_cost += average_fare * num_people

        else:
            # fallback: 연결 가능한 pair마다 계산
            ordered = sights + lunch + dinner
            for i in range(len(ordered) - 1):
                pid1 = ordered[i]['place_id']
                pid2 = ordered[i + 1]['place_id']
                lat1, lon1 = get_place_location(db, pid1)
                lat2, lon2 = get_place_location(db, pid2)
                if None in (lat1, lon1, lat2, lon2):
                    continue
                dist = haversine(lat1, lon1, lat2, lon2)
                if dist < 1.0:
                    continue
                fare = get_public_transport_fare(lat1, lon1, lat2, lon2)
                if fare == 0:
                    fare = 1250 if dist < 3 else 1800 if dist < 10 else 2500
                total_cost += fare * num_people

    return total_cost


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

def calculate_total_budget_from_schedule_id(db: Session, schedule_id: int) -> dict:
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ValueError(f"ID가 {schedule_id}인 스케줄을 찾을 수 없습니다.")

    try:
        plan_json = json.loads(schedule.schedule_json)
    except Exception as e:
        raise ValueError(f"schedule_json 파싱 실패: {e}")

    num_people = schedule.num_people or 1  # 여기서 사용자 수 받아옴

    food_cost = calculate_food_cost(db, plan_json, num_people)
    entry_fees = estimate_entry_fees(db, plan_json, num_people)
    transport_cost = calculate_transport_cost(db, plan_json, num_people=num_people)
    total_cost = food_cost + entry_fees + transport_cost


    region_names = []
    seen = set()
    for day in plan_json.values():
        for section in ["sights", "lunch", "dinner"]:
            for item in day.get(section, []):
                place = (
                    db.query(models.Destination).filter(models.Destination.place_id == item["place_id"]).first()
                    or db.query(models.Meal).filter(models.Meal.place_id == item["place_id"]).first()
                )
                area = getattr(place, "area", None)
                if area and area not in seen:
                    region_names.append(area)
                    seen.add(area)

    
    budget_comment = ask_gpt_budget_comment(total_cost, region_names, days=len(plan_json), num_people=num_people)

    return {
        "food_cost": food_cost,
        "entry_fees": entry_fees,
        "transport_cost": transport_cost,
        "total_cost": total_cost,
        "comment": budget_comment
    }

if __name__ == "__main__":
    from database import SessionLocal
    db = SessionLocal()

    schedule_id = 2
    budget = calculate_total_budget_from_schedule_id(db, schedule_id)
    print(json.dumps(budget, ensure_ascii=False, indent=2))

    saved_budget = save_budget(db, schedule_id, budget)
    print(f"Budget 저장 완료, id: {saved_budget.id}")