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

# 감정 → 추천 스타일 매핑
EMOTION_TO_STYLE = {
    "기쁜": ["activity", "hotplace", "photo", "shopping"],
    "설레는": ["date", "culture", "exotic", "landmark", "photo"],
    "평범한": ["nature", "healing", "quiet", "traditional"],
    "놀란": ["exotic", "landmark", "activity", "hotplace"],
    "불쾌한": ["healing", "quiet", "nature", "view"],
    "두려운": ["culture", "traditional", "team"],
    "슬픈": ["healing", "nature", "family", "culture", "quiet"],
    "화나는": ["activity", "shopping", "team", "photo"],
}

def get_styles_by_emotions(emotions: List[str]) -> List[str]:
    styles = []
    for emo in emotions:
        styles += EMOTION_TO_STYLE.get(emo, [])
    return list(set(styles))

class ScheduleRequest(BaseModel):
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
        LIMIT 6
    """), {"city": f"%{city}%"}).fetchall()

    meals = db.execute(text("""
        SELECT place_id, name, food_type, latitude, longitude 
        FROM meals 
        WHERE location ILIKE :city 
        LIMIT 6
    """), {"city": f"%{city}%"}).fetchall()

    accommodations = db.execute(text("""
        SELECT place_id, name, location, latitude, longitude 
        FROM accommodations 
        WHERE location ILIKE :city 
        LIMIT 2
    """), {"city": f"%{city}%"}).fetchall()

    def row_to_dict(row):
        d = dict(row._mapping)
        for k, v in d.items():
            if isinstance(v, Decimal):
                d[k] = float(v)
        return d

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
        """), {"id": place_id}).fetchone()
    return result[0] if result else None

def clean_schedule(schedule: dict, db: Session):
    valid_plans = []
    for day in schedule.get("plans", []):
        new_schedule = []
        for item in day.get("schedule", []):
            pid = str(item.get("placeId", "")).strip()
            if not pid:
                continue
            place_name = get_place_name_from_db(pid, db)
            lat = item.get("latitude")
            lng = item.get("longitude")
            if place_name and lat is not None and lng is not None:
                item["place"] = place_name
                item["placeId"] = pid
                new_schedule.append(item)
        if new_schedule:
            valid_plans.append({"day": day.get("day"), "schedule": new_schedule})
    return {
        "aiEmpathy": schedule.get("aiEmpathy"),
        "tags": schedule.get("tags"),
        "plans": valid_plans
    }

def generate_schedule_prompt(end_city, start_date, end_date,
                             emotions, companions, peopleCount, places_data) -> str:
    trip_days = calculate_trip_days(start_date, end_date)
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)
    style_list = get_styles_by_emotions(emotions)
    style_str = ", ".join(style_list)

    dest_json = json.dumps(places_data["destinations"], ensure_ascii=False)
    meals_json = json.dumps(places_data["meals"], ensure_ascii=False)
    accom_json = json.dumps(places_data["accommodations"], ensure_ascii=False)

    prompt = f"""
당신은 여행 일정 AI입니다. 아래 조건을 반드시 준수하여 **JSON으로만** 출력하세요.
도착: {end_city}
기간: {start_date} ~ {end_date} (총 {trip_days}일)
감정: {emotion_str}
추천 스타일: {style_str}
동행자: {companions_str}
인원: {peopleCount}명

조건:
- 매일 09:00 관광지 1곳, 12:00 점심 맛집 1곳, 15:00 관광지 1곳, 18:00 저녁 맛집 1곳, 21:00 숙소 1곳 포함
- 마지막 날엔 숙소 제외
- 장소는 제공된 리스트에서만 선택
- 일정은 지리적으로 인접한 순서로 배치
- 중복 장소 금지
- JSON 외 텍스트 포함 금지

[관광지 리스트]
{dest_json}

[맛집 리스트]
{meals_json}

[숙소 리스트]
{accom_json}

**반드시 아래 예시와 똑같은 키와 구조의 JSON만 출력하세요:**
```json
{{
  "aiEmpathy": "즐거운 여정을 위한 일정입니다!",
  "tags": ["힐링", "친구"],
  "plans": [
    {{
      "day": 1,
      "schedule": [
        {{
          "time": "09:00",
          "place": "경복궁",
          "placeId": "PLACE_ID_1",
          "aiComment": "역사적인 장소 방문",
          "latitude": 37.57961,
          "longitude": 126.97704
        }}
      ]
    }}
  ]
}}
"""
    return prompt.strip()

def extract_json_from_ai_response(ai_text: str) -> dict:
    match = re.search(r"```json(.*?)```", ai_text, re.DOTALL)
    if match:
        body = match.group(1)
    else:
        s = ai_text.find("{")
        e = ai_text.rfind("}")
        if s == -1 or e == -1:
            raise ValueError("JSON 구조가 없습니다.")
        body = ai_text[s:e+1]
    return json5.loads(body)


def normalize_schedule_format(data: dict) -> ScheduleAIResponse:
    plans = []
    for day in data.get("plans", []):
        items = [SchedulePlanItem(**it) for it in day.get("schedule", [])]
        plans.append(ScheduleDayPlan(day=day.get("day"), schedule=items))
    return ScheduleAIResponse(
        aiEmpathy=data.get("aiEmpathy"),
        tags=data.get("tags"),
        plans=plans
    )


def save_ai_schedule_places(plans: List[dict], db: Session):
    sched_id = str(uuid.uuid4())
    for day in plans:
        for item in day["schedule"]:
            pid = item.get("placeId")
            if not pid:
                continue
            comment = item.get("aiComment", "").lower()
            if "숙소" in comment:
                ptype = "accommodation"
            elif any(word in comment for word in ["점심", "저녁", "식사"]):
                ptype = "meal"
            else:
                ptype = "destination"
            db.execute(text("""
                INSERT INTO ai_schedule_places (schedule_id, place_id, place_type)
                VALUES (:sid, :pid, :ptype)
            """), {"sid": sched_id, "pid": pid, "ptype": ptype})
    db.commit()
    
def get_ai_schedule(db: Session, end_city: str, start_date: str, end_date: str,
                    emotions: List[str], companions: List[str], peopleCount: int) -> ScheduleAIResponse:
    places = fetch_places_from_db(db, end_city)

    prompt = generate_schedule_prompt(
        end_city, start_date, end_date,
        emotions, companions, peopleCount, places
    )
    messages = [
        {"role": "system", "content": "You are a travel planner AI."},
        {"role": "user", "content": prompt}
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.7,
        max_tokens=3000
    )
    ai_text = resp.choices[0].message.content

    parsed = extract_json_from_ai_response(ai_text)
    cleaned = clean_schedule(parsed, db)
    save_ai_schedule_places(cleaned["plans"], db)

    return normalize_schedule_format(cleaned)

app = FastAPI()

@app.post("/ai/schedule", response_model=ScheduleAPIResponse)
def api_ai_schedule(req: ScheduleRequest, db: Session = Depends(get_db)):
    try:
        ai_res = get_ai_schedule(
            db=db,
            end_city=req.endCity,
            start_date=req.startDate,
            end_date=req.endDate,
            emotions=req.emotions,
            companions=req.companions,
            peopleCount=req.peopleCount
        )
        return ScheduleAPIResponse(
            endCity=req.endCity,
            startDate=req.startDate,
            endDate=req.endDate,
            emotions=req.emotions,
            companions=req.companions,
            peopleCount=req.peopleCount,
            aiResult=ai_res
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
