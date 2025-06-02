import re
import json
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from openai import OpenAI

from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 모델 ---
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
    placeId: Optional[int]
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

# --- 감정 → 스타일 매핑 ---
EMOTION_TO_STYLE = {
    "기쁜": ["style_activity", "style_hotplace", "style_photo", "style_shopping"],
    "설레는": ["style_date", "style_culture", "style_exotic", "style_landmark", "style_photo"],
    "평범한": ["style_nature", "style_healing", "style_quiet", "style_traditional"],
    "놀란": ["style_exotic", "style_landmark", "style_activity", "style_hotplace"],
    "불쾌한": ["style_healing", "style_quiet", "style_nature", "style_view"],
    "두려운": ["style_culture", "style_traditional", "style_team"],
    "슬픈": ["style_healing", "style_nature", "style_family", "style_culture", "style_quiet"],
    "화나는": ["style_activity", "style_shopping", "style_team", "style_photo"],
    "힐링": ["style_healing", "style_nature", "style_quiet"],
}

def map_emotions_to_styles(emotions: List[str]) -> List[str]:
    styles = set()
    for emo in emotions:
        styles.update(EMOTION_TO_STYLE.get(emo, []))
    return list(styles)

def generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions, peopleCount) -> str:
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)
    return (
        f"출발지: {start_city}\n"
        f"도착지: {end_city}\n"
        f"여행 기간: {start_date}부터 {end_date}까지\n"
        f"사용자 감정: {emotion_str}\n"
        f"동행인: {companions_str}\n"
        f"인원 수: {peopleCount}명\n\n"
        "이 정보를 바탕으로 사용자에게 맞춤형 여행 일정을 추천해줘. 결과는 반드시 JSON 형식으로 출력해야 하며, 다음 조건을 따라야 해:\n\n"
        "1. \"aiEmpathy\": 사용자 감정에 공감하는 한 문장\n"
        "2. \"tags\": 여행을 대표하는 키워드 4개\n"
        "3. \"plans\": 반드시 **리스트(List)** 형식으로 작성된 각 날짜별 일정 정보\n\n"
        "⚠️ 절대로 {\"day1\": {...}, \"day2\": {...}} 같은 객체(Dictionary) 형태로 작성하지 말 것\n\n"
        "각 plans 항목은 다음과 같은 구조여야 함:\n"
        "- day: 날짜 숫자\n"
        "- schedule: 하루 일정 리스트. 각 일정 항목은 다음 필드 포함:\n"
        "  - time, place, placeId, aiComment, latitude, longitude\n\n"
        "예시:\n"
        "```json\n"
        "{\n"
        "  \"aiEmpathy\": \"힐링과 즐거움을 모두 느낄 수 있는 여행을 준비했어요!\",\n"
        "  \"tags\": [\"힐링\", \"자연\", \"맛집\", \"여유\"],\n"
        "  \"plans\": [\n"
        "    {\n"
        "      \"day\": 1,\n"
        "      \"schedule\": [\n"
        "        {\n"
        "          \"time\": \"09:00\",\n"
        "          \"place\": \"호텔 부산\",\n"
        "          \"placeId\": 123,\n"
        "          \"aiComment\": \"여유로운 하루의 시작\",\n"
        "          \"latitude\": 35.1531,\n"
        "          \"longitude\": 129.0604\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n"
        "이 구조를 반드시 그대로 따를 것!"
    )

def extract_json_from_ai_response(ai_response_text: str) -> dict:
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, ai_response_text, re.DOTALL)
    json_str = match.group(1).strip() if match else ai_response_text.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n원본:\n{json_str[:300]}...")

def normalize_schedule_format(response_json: dict) -> ScheduleAIResponse:
    import re

    raw_plans = response_json.get("plans")
    if not raw_plans:
        raise ValueError("plans 데이터가 존재하지 않습니다.")

    plans_list = []

    if isinstance(raw_plans, dict):
        # dict -> 리스트 변환
        for day_key in sorted(raw_plans.keys(), key=lambda x: int(re.sub(r"\D", "", x))):
            day_data = raw_plans[day_key]
            plans_list.append(ScheduleDayPlan(
                day=int(re.sub(r"\D", "", day_key)),
                schedule=[SchedulePlanItem(**item) for item in day_data.get("schedule", [])]
            ))
    elif isinstance(raw_plans, list):
        # 리스트일 경우 각 항목을 Pydantic 객체로 변환
        for day_item in raw_plans:
            plans_list.append(ScheduleDayPlan(
                day=day_item.get("day"),
                schedule=[SchedulePlanItem(**item) for item in day_item.get("schedule", [])]
            ))
    else:
        raise ValueError("plans 형식이 유효하지 않습니다.")

    return ScheduleAIResponse(
        aiEmpathy=response_json.get("aiEmpathy", ""),
        tags=response_json.get("tags", []),
        plans=plans_list
    )

def get_ai_schedule(
    db: Session,
    start_city: str,
    end_city: str,
    start_date: str,
    end_date: str,
    emotions: List[str],
    companions: List[str],
    peopleCount: int
) -> ScheduleAIResponse:
    styles = map_emotions_to_styles(emotions)
    prompt = generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions, peopleCount)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful travel itinerary planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    raw_text = response.choices[0].message.content
    print("GPT 응답:\n", raw_text)

    json_data = extract_json_from_ai_response(raw_text)
    normalized = normalize_schedule_format(json_data)

    return ScheduleAIResponse(
        aiEmpathy=normalized.aiEmpathy,
        tags=normalized.tags,
        plans=normalized.plans
    )

# --- FastAPI 엔드포인트 ---
app = FastAPI()

@app.post("/api/schedule", response_model=ScheduleAPIResponse)
def create_schedule(request: ScheduleRequest, db: Session = Depends(get_db)):
    try:
        ai_result = get_ai_schedule(
            db=db,
            start_city=request.startCity,
            end_city=request.endCity,
            start_date=request.startDate,
            end_date=request.endDate,
            emotions=request.emotions,
            companions=request.companions,
            peopleCount=request.peopleCount
        )
        return ScheduleAPIResponse(
            startCity=request.startCity,
            endCity=request.endCity,
            startDate=request.startDate,
            endDate=request.endDate,
            emotions=request.emotions,
            companions=request.companions,
            peopleCount=request.peopleCount,
            aiResult=ai_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 또는 파싱 실패: {str(e)}")
