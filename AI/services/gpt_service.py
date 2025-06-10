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

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 데이터베이스 엔진 및 세션 설정
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    DB 세션을 생성하고 반환하는 의존성 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 사용자 요청 모델
class ScheduleRequest(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    emotions: List[str]
    companions: List[str]
    peopleCount: int

# AI 응답 내 일정 아이템 모델
class SchedulePlanItem(BaseModel):
    time: Optional[str]
    place: Optional[str]
    placeId: Optional[str]
    aiComment: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

# 하루 일정 모델
class ScheduleDayPlan(BaseModel):
    day: int
    schedule: List[SchedulePlanItem]

# AI 전체 응답 모델
class ScheduleAIResponse(BaseModel):
    aiEmpathy: Optional[str]
    tags: Optional[List[str]]
    plans: List[ScheduleDayPlan]

# API 응답 모델
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
    """
    시작 날짜와 종료 날짜를 받아 여행 일수를 계산 (최소 1일)
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return max((end - start).days + 1, 1)
    except Exception:
        return 1


def fetch_places_from_db(db: Session, city: str):
    """
    DB에서 해당 도시의 관광지, 맛집, 숙소 데이터를 조회
    """
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
    """
    place_id를 받아 DB에서 해당 장소명을 반환
    """
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
    """
    AI 응답에서 유효하지 않은 placeId 항목 제거, 장소명 매핑 및 좌표 유효성 검증
    """
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
            # 장소명과 좌표 모두 유효해야 추가
            if place_name and lat is not None and lng is not None:
                item["place"] = place_name
                item["placeId"] = pid
                new_schedule.append(item)
        if new_schedule:
            valid_plans.append({"day": day.get("day"), "schedule": new_schedule})
    return {"aiEmpathy": schedule.get("aiEmpathy"),
            "tags": schedule.get("tags"),
            "plans": valid_plans}

def generate_schedule_prompt(start_city, end_city, start_date, end_date,
                             emotions, companions, peopleCount, places_data) -> str:
    """
    AI에게 전달할 프롬프트 생성. 일정은 아래 순서로 구성해야 함:
      - 09:00 관광지 1곳
      - 12:00 점심 맛집 1곳
      - 15:00 관광지 1곳
      - 18:00 저녁 맛집 1곳
      - 21:00 숙소 1곳 (마지막 날엔 제외)
    지리적으로 가까운 순서로 일정을 배치하고, JSON 형태로만 출력해야 함.
    """
    trip_days = calculate_trip_days(start_date, end_date)
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)

    dest_json = json.dumps(places_data["destinations"], ensure_ascii=False, indent=2)
    meals_json = json.dumps(places_data["meals"], ensure_ascii=False, indent=2)
    accom_json = json.dumps(places_data["accommodations"], ensure_ascii=False, indent=2)

    prompt = f"""
당신은 여행 일정 AI입니다. 아래 조건을 반드시 준수하여 **JSON으로만** 출력하세요.
출발: {start_city}, 도착: {end_city}
기간: {start_date} ~ {end_date} (총 {trip_days}일)
감정: {emotion_str}
동행자: {companions_str}
인원: {peopleCount}명

조건:
- 매일 09:00 관광지 1곳, 12:00 점심 맛집 1곳, 15:00 관광지 1곳, 18:00 저녁 맛집 1곳, 21:00 숙소 1곳을 포함
- 마지막 날에는 숙소를 제외
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

**반드시 아래 예시와 똑같은 키와 구조의 JSON만** 출력하세요:
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
        }},
        {{
          "time": "12:00",
          "place": "종로 전통 맛집",
          "placeId": "PLACE_ID_2",
          "aiComment": "전통 한식 체험",
          "latitude": 37.57004,
          "longitude": 126.97690
        }},
        … (중략) …
      ]
    }},
    … (중략) …
  ]
}}
"""
    return prompt.strip()


def extract_json_from_ai_response(ai_text: str) -> dict:
    """
    AI 응답에서 JSON 부분을 추출하여 dict로 반환
    """
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
    """
    추출된 dict를 Pydantic 모델로 변환
    """
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
    """
    일정 로그를 DB에 저장
    """
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


def get_ai_schedule(db: Session, start_city: str, end_city: str, start_date: str, end_date: str,
                    emotions: List[str], companions: List[str], peopleCount: int) -> ScheduleAIResponse:
    """
    전체 일정 생성 로직
    """
    # DB에서 장소 데이터 조회
    places = fetch_places_from_db(db, end_city)

    # AI용 프롬프트 생성
    prompt = generate_schedule_prompt(
        start_city, end_city, start_date, end_date,
        emotions, companions, peopleCount, places
    )
    messages = [
        {"role": "system", "content": "You are a travel planner AI."},
        {"role": "user", "content": prompt}
    ]

    # AI 호출
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=3000
    )
    ai_text = resp.choices[0].message.content

    # AI 응답 파싱 및 스케줄 정리
    parsed = extract_json_from_ai_response(ai_text)
    cleaned = clean_schedule(parsed, db)

    # 일정 로그 저장
    save_ai_schedule_places(cleaned["plans"], db)

    # Pydantic 모델로 변환하여 반환
    return normalize_schedule_format(cleaned)

# FastAPI 엔드포인트 정의
app = FastAPI()

@app.post("/ai/schedule", response_model=ScheduleAPIResponse)
def api_ai_schedule(req: ScheduleRequest, db: Session = Depends(get_db)):
    """
    여행 일정을 생성하여 반환
    """
    try:
        ai_res = get_ai_schedule(
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
            aiResult=ai_res
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")