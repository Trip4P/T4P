import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict
import math
import json
from sqlalchemy.orm import Session
from openai import OpenAI
from config import settings
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
    for day, schedule in plan_json.items():
        for item in schedule:
            meal = db.query(models.Meal).filter(models.Meal.place_id == item['place_id']).first()
            if meal:
                avg_price = price_map.get(meal.price_level, 0)
                total_cost += avg_price * num_people
    return total_cost

def ask_gpt_for_entry_fee(place_name: str) -> int:
    prompt = f"'{place_name}'에 입장료가 있다면 대략 얼마일지 추정해줘. (한국 원화 기준으로 숫자만 답변해줘)"
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
        fee = int(response.choices[0].message.content.strip())
    except Exception:
        fee = 0
    return fee

def estimate_entry_fees(db: Session, plan_json: dict) -> int:
    total_fee = 0
    for day, schedule in plan_json.items():
        for item in schedule:
            destination = db.query(models.Destination).filter(models.Destination.place_id == item['place_id']).first()
            if destination:
                fee = ask_gpt_for_entry_fee(destination.name)
                total_fee += fee
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
    for day, places in plan_json.items():
        for i in range(len(places) - 1):
            from_id = places[i]['place_id']
            to_id = places[i + 1]['place_id']

            lat1, lon1 = get_place_location(db, from_id)
            lat2, lon2 = get_place_location(db, to_id)

            if None in (lat1, lon1, lat2, lon2):
                continue

            dist = haversine(lat1, lon1, lat2, lon2)
            if dist < 1.0:
                continue

            fare = get_public_transport_fare(lat1, lon1, lat2, lon2)
            total_cost += fare * num_people  # ✅ 인원 수 반영
    return total_cost


def ask_gpt_budget_comment(user_budget: int, region_names: List[str], days: int = 2, num_people: int = 1) -> str:
    region_str = ", ".join(region_names)
    prompt = f"""
    사용자가 {region_str} 지역을 {days}일 동안 {num_people}명이 여행할 예정이에요.
    총 예산은 {user_budget}원이에요.
    해당 지역의 평균 여행 비용과 비교해서 이 예산이 충분한지, 부족한지 판단해주고,
    친절한 말투로 짧은 코멘트를 작성해줘.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은  예산 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
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

    num_people = schedule.num_people or 1  # ← 여기서 사용자 수 적용

    # 이하 생략 (계산 로직 동일)


    food_cost = calculate_food_cost(db, plan_json, num_people)
    entry_fees = estimate_entry_fees(db, plan_json)
    transport_cost = calculate_transport_cost(db, plan_json, num_people=num_people)
    total_cost = food_cost + entry_fees + transport_cost

    region_names = []
    for day in plan_json.values():
        for item in day:
            place = db.query(models.Destination).filter(models.Destination.place_id == item["place_id"]).first()
            if not place:
                place = db.query(models.Meal).filter(models.Meal.place_id == item["place_id"]).first()

            loc = getattr(place, "location", None)
            if loc:
            # loc 예: "서울 종로구 삼청동" -> "서울 종로구"까지만 자르기
            # 구 단위까지만 추출 (앞에서 두 단어까지)
                region = ' '.join(loc.split()[:2])
                if region not in region_names:
                    region_names.append(region)


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
    print(f"Budget 저장 완료, id: {saved_budget.id}, comment: {saved_budget.comment}")
