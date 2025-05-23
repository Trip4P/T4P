from typing import List, Dict
from sqlalchemy.orm import Session
import models
import math
from openai import OpenAI
from config import settings

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
    for day in plan_json.get("plans", []):
        for item in day.get("schedule", []):
            if "식사" in item.get("placeType", ""):
                meal = db.query(models.Meal).filter(models.Meal.place_id == item['placeId']).first()
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
    for day in plan_json.get("plans", []):
        for item in day.get("schedule", []):
            # 식사는 food cost에서 처리하니까, 여기선 관광지만 계산
            destination = db.query(models.Destination).filter(models.Destination.place_id == item['placeId']).first()
            if destination:
                total_fee += ask_gpt_for_entry_fee(destination.name)
    return total_fee

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반경 (km)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def calculate_transport_cost(db: Session, plan_json: dict) -> int:
    total_cost = 0
    for day in plan_json.get("plans", []):
        places = day.get("schedule", [])
        for i in range(len(places) - 1):
            from_place = db.query(models.Destination).filter(models.Destination.id == places[i]['placeId']).first()
            to_place = db.query(models.Destination).filter(models.Destination.id == places[i+1]['placeId']).first()
            if from_place and to_place:
                lat1, lon1 = from_place.latitude, from_place.longitude
                lat2, lon2 = to_place.latitude, to_place.longitude
                if None in (lat1, lon1, lat2, lon2):
                    continue  # 위도경도 정보 없으면 계산 제외
                dist = haversine(lat1, lon1, lat2, lon2)
                cost = 1250  # 기본요금
                extra_fee = 0
                if dist > 5:
                    extra_fee = int((dist - 5) // 5) * 100
                total_cost += cost + extra_fee
    return total_cost
