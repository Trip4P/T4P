import re
import json, json5
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
    print(f"[DEBUG] 도시 필터: {city}")

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

    print(f"[DEBUG] 관광명소 개수: {len(destinations)}")
    print(f"[DEBUG] 맛집 개수: {len(meals)}")
    print(f"[DEBUG] 숙소 개수: {len(accommodations)}")

    return {
        "destinations": [row_to_dict(r) for r in destinations],
        "meals": [row_to_dict(r) for r in meals],
        "accommodations": [row_to_dict(r) for r in accommodations],
    }

def row_to_dict(row):
    result = dict(row._mapping)
    for k, v in result.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
    return result

def get_place_name_from_db(place_id: str, db: Session):
    result = db.execute(
        text("""
            SELECT name FROM meals WHERE place_id = :id
            UNION
            SELECT name FROM destinations WHERE place_id = :id
            UNION
            SELECT name FROM accommodations WHERE place_id = :id
        """),
        {"id": place_id}  # 여기도 문자열로 전달됨
    ).fetchone()

    return result[0] if result else None

def clean_schedule(schedule: dict, db: Session):
    for day in schedule.get("plans", []):
        for item in day.get("schedule", []):
            place_id = item.get("placeId")
            if place_id is None:
                raise ValueError(f"placeId가 비어 있음: {place_id}")

            place_id_str = str(place_id).strip()
            if not place_id_str:
                raise ValueError(f"placeId가 비어 있거나 유효하지 않음: {place_id}")

            item['placeId'] = place_id_str  # placeId 문자열로 고정

            # place 필드가 '미확인 장소 ID'로 시작하면 DB에서 조회
            if item.get("place", "").startswith("미확인 장소 ID"):
                place_name = get_place_name_from_db(place_id_str, db)
                if place_name:
                    item["place"] = place_name
                else:
                    # DB에 없으면 그대로 둬도 됨 또는 기본 메시지로 변경
                    item["place"] = f"미확인 장소 ID {place_id_str}"

    return schedule

def generate_schedule_prompt(start_city, end_city, start_date, end_date,
                             emotions, companions, peopleCount, places_data) -> str:
    trip_days = calculate_trip_days(start_date, end_date)
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)

    # indent 추가로 구조적 가독성 확보
    destinations_json = json.dumps(places_data["destinations"], ensure_ascii=False, indent=2)
    meals_json = json.dumps(places_data["meals"], ensure_ascii=False, indent=2)
    accommodations_json = json.dumps(places_data["accommodations"], ensure_ascii=False, indent=2)

    prompt = f"""
당신은 여행 일정 계획을 생성하는 AI입니다.
아래 조건을 **절대로 어기지 말고**, 반드시 **JSON 형태로만** 출력하세요.  
✅ JSON 외 어떤 설명 텍스트도 포함하지 마세요!

출발지: {start_city}
도착지: {end_city}
여행 기간: {start_date}부터 {end_date}까지, 총 {trip_days}일
사용자 감정: {emotion_str}
동행인: {companions_str}
인원 수: {peopleCount}명

🟨 아래는 일정 생성에 사용할 장소 데이터입니다. 반드시 이 안의 장소만 사용하세요.
🟥 **절대로 새로운 장소를 상상해서 만들지 마세요.**
🟥 **`name`, `placeId`, `latitude`, `longitude`는 아래 데이터에 있는 값을 그대로 사용하세요.**
🟥 **`placeId`는 GPT가 직접 만들지 마세요. 무조건 데이터에 있는 값을 그대로 쓰세요.**

관광명소 데이터:
{destinations_json}

맛집 데이터:
{meals_json}

숙소 데이터:
{accommodations_json}

📋 일정 생성 규칙:
- 각 날짜는 아래 장소를 포함해야 합니다:
  - 관광지 1곳 (관광명소 데이터에서 선택)
  - 점심 식사 장소 1곳 (맛집 데이터에서 선택)
  - 저녁 식사 장소 1곳 (맛집 데이터에서 선택)
  - 숙소 1곳 (숙소 데이터에서 선택)
- 장소는 하루 안에서 중복 없이 사용해야 하며, 가급적 전체 일정에서 중복을 피하세요.
- 일정은 시간 순서대로 정렬되어야 합니다.
- 출력 형식은 아래 JSON 예시와 정확히 일치해야 합니다.

🧾 JSON 출력 예시:

```json
{{
  "aiEmpathy": "즐거운 여행이 되도록 정성껏 준비했어요!",
  "tags": ["자연", "맛집", "힐링", "감성"],
  "plans": [
    {{
      "day": 1,
      "schedule": [
        {{
          "time": "09:00",
          "place": "경복궁",
          "placeId": 734,
          "aiComment": "자연과 역사가 어우러진 경복궁에서 아침을 시작하세요.",
          "latitude": 37.5796,
          "longitude": 126.977
        }},
        {{
          "time": "12:00",
          "place": "광화문맛집",
          "placeId": 910,
          "aiComment": "광화문에서 현지 맛집을 경험하세요.",
          "latitude": 37.570,
          "longitude": 126.976
        }},
        {{
          "time": "18:00",
          "place": "명동식당",
          "placeId": 911,
          "aiComment": "명동 거리에서 저녁 식사를 즐기세요.",
          "latitude": 37.560,
          "longitude": 126.985
        }},
        {{
          "time": "20:00",
          "place": "서울호텔",
          "placeId": 1203,
          "aiComment": "편안한 서울호텔에서 하루를 마무리하세요.",
          "latitude": 37.565,
          "longitude": 126.978
        }}
      ]
    }}
  ]
}}
"""
    return prompt.strip()

def extract_json_from_ai_response(ai_response_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", ai_response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # 혹시 JSON 블록 감싸는 마크다운 없으면
        json_start = ai_response_text.find("{")
        json_end = ai_response_text.rfind("}")
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            raise ValueError("JSON 구조 시작/종료가 올바르지 않습니다.")
        json_str = ai_response_text[json_start:json_end + 1]

    try:
        return json5.loads(json_str)
    except Exception as e:
        preview = json_str[:500].replace("\n", "\\n")
        raise ValueError(f"json5 파싱 실패: {e}\n원본 일부:\n{preview}")

def normalize_schedule_format(response_json: dict) -> ScheduleAIResponse:
    raw_plans = response_json.get("plans")
    if not raw_plans:
        raise ValueError("plans 항목이 없습니다.")

    plans = []
    for day_item in raw_plans:
        schedule = [SchedulePlanItem(**item) for item in day_item.get("schedule", [])]
        plans.append(ScheduleDayPlan(day=day_item.get("day"), schedule=schedule))

    return ScheduleAIResponse(
        aiEmpathy=response_json.get("aiEmpathy", ""),
        tags=response_json.get("tags", []),
        plans=plans
    )

def map_ai_places_to_db_places(ai_plans, places_data):
    placeid_to_place = {}
    for category in ['destinations', 'meals', 'accommodations']:
        for place in places_data[category]:
            placeid_to_place[str(place['place_id'])] = place  # 반드시 str로

    for day_plan in ai_plans:
        for item in day_plan['schedule']:
            place_id = item.get('placeId')
            if place_id is not None:
                place_id_str = str(place_id)
                if place_id_str in placeid_to_place:
                    db_place = placeid_to_place[place_id_str]
                    item['place'] = db_place['name']
                    item['latitude'] = db_place.get('latitude')
                    item['longitude'] = db_place.get('longitude')
                else:
                    print(f"[WARNING] placeId {place_id}가 DB에 없습니다.")
                    item['place'] = f"미확인 장소 ID {place_id}"
                    item['latitude'] = None
                    item['longitude'] = None
            else:
                print("[WARNING] placeId가 없습니다.")
    return ai_plans

def get_ai_schedule(db: Session,
                    start_city: str,
                    end_city: str,
                    start_date: str,
                    end_date: str,
                    emotions: List[str],
                    companions: List[str],
                    peopleCount: int) -> ScheduleAIResponse:
    try:
        print("[DEBUG] get_ai_schedule 시작")

        places_data = fetch_places_from_db(db, end_city)
        print(f"[DEBUG] 장소 데이터 로드 완료 - 관광명소 {len(places_data['destinations'])}, 맛집 {len(places_data['meals'])}, 숙소 {len(places_data['accommodations'])}")

        prompt = generate_schedule_prompt(
            start_city, end_city, start_date, end_date,
            emotions, companions, peopleCount, places_data
        )
        print("[DEBUG] 프롬프트 생성 완료")

        messages = [
            {"role": "system", "content": "You are a travel planner AI that generates user-personalized travel itineraries based on given data."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )
        print("[DEBUG] GPT 응답 수신 완료")

        ai_text = response.choices[0].message.content
        print("[DEBUG] GPT 응답 내용:\n", ai_text[:500])  # 너무 길면 잘라서 출력

        parsed_json = extract_json_from_ai_response(ai_text)
        print("[DEBUG] JSON 파싱 완료")

        mapped_plans = map_ai_places_to_db_places(parsed_json['plans'], places_data)
        print("[DEBUG] 장소 매핑 완료")

        parsed_json['plans'] = mapped_plans

        cleaned = clean_schedule(parsed_json, db)
        print("[DEBUG] 스케줄 정리 완료")

        result = normalize_schedule_format(parsed_json)
        print("[DEBUG] 일정 포맷 정규화 완료")

        return result

    except Exception as e:
        import traceback
        print("[ERROR] get_ai_schedule에서 예외 발생:")
        traceback.print_exc()
        raise


app = FastAPI()

@app.post("/api/ai/schedule", response_model=ScheduleAPIResponse)
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
        traceback.print_exc()  # ✅ 실제 오류 출력
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
