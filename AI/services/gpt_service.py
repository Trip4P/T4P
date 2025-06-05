import re
import json, json5
import uuid
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from openai import OpenAI

from config import settings  # OPENAI_API_KEY, DATABASE_URL 포함

client = OpenAI(api_key=settings.OPENAI_API_KEY)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScheduleRequest(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    emotions: List[str]
    companions: List[str]
    peopleCount: int

class SchedulePlanItem(BaseModel):
    time: Optional[str]
    place: Optional[str]
    placeId: Optional[str]
    aiComment: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class ScheduleDayPlan(BaseModel):
    day: int
    schedule: List[SchedulePlanItem]

class ScheduleAIResponse(BaseModel):
    aiEmpathy: Optional[str]
    tags: Optional[List[str]]
    plans: List[ScheduleDayPlan]

class ScheduleAPIResponse(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    emotions: List[str]
    companions: List[str]
    peopleCount: int
    aiResult: ScheduleAIResponse

def calculate_trip_days(start_date: str, end_date: str) -> int:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return max((end - start).days + 1, 1)
    except Exception:
        return 1

def fetch_places_from_db(db: Session, city: str):
    destinations = db.execute(text("""
        SELECT place_id, name, area, latitude, longitude 
        FROM destinations 
        WHERE area ILIKE :city 
        LIMIT 30
    """), {"city": f"%{city}%"}).fetchall()

    meals = db.execute(text("""
        SELECT place_id, name, food_type, latitude, longitude 
        FROM meals 
        WHERE location ILIKE :city 
        LIMIT 20
    """), {"city": f"%{city}%"}).fetchall()

    accommodations = db.execute(text("""
        SELECT place_id, name, location, latitude, longitude 
        FROM accommodations 
        WHERE location ILIKE :city 
        LIMIT 10
    """), {"city": f"%{city}%"}).fetchall()

    def row_to_dict(row):
        result = dict(row._mapping)
        for k, v in result.items():
            if isinstance(v, Decimal):
                result[k] = float(v)
        return result

    return {
        "destinations": [row_to_dict(r) for r in destinations],
        "meals": [row_to_dict(r) for r in meals],
        "accommodations": [row_to_dict(r) for r in accommodations],
    }

def get_place_name_from_db(place_id: str, db: Session):
    result = db.execute(
        text("""
            SELECT name FROM meals WHERE place_id = :id
            UNION
            SELECT name FROM destinations WHERE place_id = :id
            UNION
            SELECT name FROM accommodations WHERE place_id = :id
        """),
        {"id": place_id}
    ).fetchone()
    return result[0] if result else None

def clean_schedule(schedule: dict, db: Session):
    valid_schedule = []
    for day in schedule.get("plans", []):
        new_day_schedule = []
        for item in day.get("schedule", []):
            place_id = item.get("placeId")
            if not place_id:
                continue

            place_id = str(place_id).strip()
            item['placeId'] = place_id

            place_name = get_place_name_from_db(place_id, db)
            if place_name:
                item["place"] = place_name
                new_day_schedule.append(item)
            else:
                print(f"DB에 없는 placeId 제거됨: {place_id}")

        if new_day_schedule:
            day["schedule"] = new_day_schedule
            valid_schedule.append(day)

    schedule["plans"] = valid_schedule
    return schedule

def generate_schedule_prompt(start_city, end_city, start_date, end_date,
                             emotions, companions, peopleCount, places_data) -> str:
    trip_days = calculate_trip_days(start_date, end_date)
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)

    destinations_json = json.dumps(places_data["destinations"], ensure_ascii=False, indent=2)
    meals_json = json.dumps(places_data["meals"], ensure_ascii=False, indent=2)
    accommodations_json = json.dumps(places_data["accommodations"], ensure_ascii=False, indent=2)

    prompt = f"""
당신은 여행 일정 계획을 생성하는 AI입니다.
**반드시 아래 조건을 지켜 JSON 형태로만 출력하세요.**

출발지: {start_city}
도착지: {end_city}
여행 기간: {start_date}부터 {end_date}까지, 총 {trip_days}일
감정: {emotion_str}
동행자: {companions_str}
인원: {peopleCount}명

**조건:**
- 아래 제공된 관광지, 맛집, 숙소 리스트에서만 장소를 선택해야 합니다.
- 목록에 없는 장소나 placeId를 생성하면 안 됩니다.
- 총 {trip_days}일에 맞춰 일정을 생성하세요.
- 하루 일정에는 관광지 1곳, 점심 식사 1곳, 저녁 식사 1곳, 숙소 1곳을 포함하세요.
- 각 날짜는 "day": 1, 2, 3, ... 으로 구분하며, 날짜 수만큼 반드시 생성하세요.
- 장소는 전체 일정에서 중복 없이 선택하세요.
- JSON 외 텍스트는 절대 포함하지 마세요. 응답은 {{ 로 시작해 }} 로 끝나야 합니다.

[관광지 리스트]
{destinations_json}

[맛집 리스트]
{meals_json}

[숙소 리스트]
{accommodations_json}

**출력 예시:**
{{
  "aiEmpathy": "즐거운 여정을 위한 일정입니다!",
  "tags": ["자연", "맛집"],
  "plans": [
    {{
      "day": 1,
      "schedule": [
        {{
          "time": "09:00",
          "place": "경복궁",
          "placeId": "PLACE_ID_1",
          "aiComment": "역사적인 장소 방문",
          "latitude": 37.5,
          "longitude": 126.9
        }}
      ]
    }}
  ]
}}
"""
    return prompt.strip()

def extract_json_from_ai_response(ai_response_text: str) -> dict:
    try:
        match = re.search(r"```json\s*(\{.*?\})\s*```", ai_response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_start = ai_response_text.find("{")
            json_end = ai_response_text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("JSON 구조가 올바르지 않습니다.")
            json_str = ai_response_text[json_start:json_end + 1]

        return json5.loads(json_str)

    except Exception as e:
        print("AI 응답 파싱 오류:", e)
        raise ValueError("AI 응답을 JSON으로 변환하는 데 실패했습니다.")

def normalize_schedule_format(response_json: dict) -> ScheduleAIResponse:
    plans = []
    for day_item in response_json.get("plans", []):
        schedule = [SchedulePlanItem(**item) for item in day_item.get("schedule", [])]
        plans.append(ScheduleDayPlan(day=day_item.get("day"), schedule=schedule))
    return ScheduleAIResponse(
        aiEmpathy=response_json.get("aiEmpathy", ""),
        tags=response_json.get("tags", []),
        plans=plans
    )

def remove_duplicate_places(plans: List[dict]) -> List[dict]:
    seen_ids = set()
    for day in plans:
        unique_schedule = []
        for item in day["schedule"]:
            pid = item.get("placeId")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                unique_schedule.append(item)
        day["schedule"] = unique_schedule
    return plans

def map_ai_places_to_db_places(ai_plans, places_data):
    placeid_to_place = {}
    for category in ['destinations', 'meals', 'accommodations']:
        for place in places_data[category]:
            placeid_to_place[str(place['place_id'])] = place

    for day_plan in ai_plans:
        for item in day_plan['schedule']:
            place_id = item.get('placeId')
            if place_id:
                place_id_str = str(place_id)
                if place_id_str in placeid_to_place:
                    db_place = placeid_to_place[place_id_str]
                    item['place'] = db_place['name']
                    item['latitude'] = db_place.get('latitude')
                    item['longitude'] = db_place.get('longitude')
                else:
                    item['place'] = f"미확인 장소 ID {place_id}"
                    item['latitude'] = None
                    item['longitude'] = None
    return ai_plans

def save_ai_schedule_places(plans: List[dict], db: Session):
    schedule_id = str(uuid.uuid4())  # 일정 단위 UUID 생성

    for day in plans:
        for item in day["schedule"]:
            place_id = item.get("placeId")
            ai_comment = item.get("aiComment", "").lower()

            if not place_id:
                continue

            # 장소 유형 추정
            if "숙소" in ai_comment:
                place_type = "accommodation"
            elif "점심" in ai_comment or "저녁" in ai_comment or "식사" in ai_comment:
                place_type = "meal"
            else:
                place_type = "destination"

            db.execute(text("""
                INSERT INTO ai_schedule_places (schedule_id, place_id, place_type)
                VALUES (:schedule_id, :place_id, :place_type)
            """), {
                "schedule_id": schedule_id,
                "place_id": place_id,
                "place_type": place_type
            })

    db.commit()

def get_ai_schedule(db: Session, start_city: str, end_city: str, start_date: str, end_date: str,
                    emotions: List[str], companions: List[str], peopleCount: int) -> ScheduleAIResponse:
    places_data = fetch_places_from_db(db, end_city)
    prompt = generate_schedule_prompt(start_city, end_city, start_date, end_date,
                                      emotions, companions, peopleCount, places_data)
    messages = [
        {"role": "system", "content": "You are a travel planner AI that generates user-personalized travel itineraries based on given data."},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=3000,
    )

    ai_text = response.choices[0].message.content
    print("AI 응답 내용:\n", ai_text)
    parsed_json = extract_json_from_ai_response(ai_text)
    parsed_json['plans'] = remove_duplicate_places(parsed_json['plans'])
    mapped_plans = map_ai_places_to_db_places(parsed_json['plans'], places_data)
    parsed_json['plans'] = mapped_plans
    cleaned = clean_schedule(parsed_json, db)

    #  인기 장소 로그 저장
    save_ai_schedule_places(cleaned['plans'], db)

    return normalize_schedule_format(cleaned)


app = FastAPI()

@app.post("/ai/schedule", response_model=ScheduleAPIResponse)
def api_ai_schedule(req: ScheduleRequest, db: Session = Depends(get_db)):
    try:
        ai_result = get_ai_schedule(
            db=db,
            start_city=req.startCity,
            end_city=req.endCity,
            start_date=req.startDate,
            end_date=req.endDate,
            emotions=req.emotions,
            companions=req.companions,
            peopleCount=req.peopleCount
        )
        return ScheduleAPIResponse(
            startCity=req.startCity,
            endCity=req.endCity,
            startDate=req.startDate,
            endDate=req.endDate,
            emotions=req.emotions,
            companions=req.companions,
            peopleCount=req.peopleCount,
            aiResult=ai_result
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
