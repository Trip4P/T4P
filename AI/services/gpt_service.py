import re
import json
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from openai import OpenAI

# 설정값 (환경변수나 config에서 관리)
from config import settings


# --- OpenAI 클라이언트 초기화 ---
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# --- DB 세션 생성기 ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Pydantic 모델 정의 ---

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
    plans: dict  # plans는 key=day1, day2 ... dict 형태


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


def generate_schedule_prompt(
    start_city: str,
    end_city: str,
    start_date: str,
    end_date: str,
    emotions: List[str],
    companions: List[str],
    peopleCount: int
) -> str:
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)
    return (
        f"출발지: {start_city}\n"
        f"도착지: {end_city}\n"
        f"여행 기간: {start_date}부터 {end_date}까지\n"
        f"사용자 감정: {emotion_str}\n"
        f"동행인: {companions_str}\n"
        f"인원 수: {peopleCount}명\n\n"
        "이 정보를 기반으로 사용자에게 맞춤형 여행 일정을 추천해줘.\n"
        "각 날짜(day1, day2, ...)별로 일정(schedule)을 구성해줘. 각 일정 항목은 다음 필드를 포함해야 해:\n"
        "- time: \"09:00\" 형식의 시간\n"
        "- place: 장소 이름\n"
        "- placeId: 숫자 ID 예: 123\n"
        "- aiComment: 해당 장소 추천 이유나 코멘트\n"
        "- latitude: 위도 값 (예: 37.5244965)\n"
        "- longitude: 경도 값 (예: 127.0414635)\n\n"
        "또한 사용자의 감정에 공감하는 한 문장(aiEmpathy)과 여행을 대표하는 키워드 4개(tags) 리스트도 포함해줘.\n\n"
        "반드시 아래 JSON 형식을 따르고, 코드블록으로 감싸서 출력해줘:\n"
        "```json\n"
        "{\n"
        "  \"aiEmpathy\": \"와아~ 지금 기분이 너무 좋은 거잖아? 😆 ...\",\n"
        "  \"tags\": [\"미식\", \"감성\", \"바다\", \"여유\"],\n"
        "  \"plans\": {\n"
        "    \"day1\": {\n"
        "      \"schedule\": [\n"
        "        {\n"
        "          \"time\": \"09:00\",\n"
        "          \"place\": \"호텔 부산\",\n"
        "          \"placeId\": 213,\n"
        "          \"aiComment\": \"오션뷰 객실에서 여유로운 시작\",\n"
        "          \"latitude\": 37.5244965,\n"
        "          \"longitude\": 127.0414635\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  }\n"
        "}\n"
        "```\n"
        "반드시 올바른 JSON 코드블록으로만 출력해줘."
    )


def extract_json_from_ai_response(ai_response_text: str) -> dict:
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, ai_response_text, re.DOTALL)
    json_str = match.group(1).strip() if match else ai_response_text.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("JSON 파싱 실패:", e)
        print("파싱 대상 텍스트:", json_str)
        raise ValueError(f"JSON 파싱 실패: {e}")

def normalize_schedule_format(response_json: dict) -> dict:
    plans_data = response_json.get("plans", {})
    plans = {}

    if not plans_data:
        # plans가 없거나 비어있으면 기본 값 처리 또는 예외 발생
        raise ValueError("기본 일정(plans) 데이터가 비어 있습니다.")

    if isinstance(plans_data, list):
        for idx, day_val in enumerate(plans_data, start=1):
            key = f"day{idx}"
            schedule_list = []
            for item in day_val.get("schedule", []):
                schedule_list.append({
                    "time": item.get("time", ""),
                    "place": item.get("place", ""),
                    "placeId": item.get("placeId", 0),
                    "aiComment": item.get("aiComment", ""),
                    "latitude": item.get("latitude", 0.0),
                    "longitude": item.get("longitude", 0.0)
                })
            plans[key] = {"schedule": schedule_list}

    elif isinstance(plans_data, dict):
        for day_key, day_val in plans_data.items():
            schedule_list = []
            for item in day_val.get("schedule", []):
                schedule_list.append({
                    "time": item.get("time", ""),
                    "place": item.get("place", ""),
                    "placeId": item.get("placeId", 0),
                    "aiComment": item.get("aiComment", ""),
                    "latitude": item.get("latitude", 0.0),
                    "longitude": item.get("longitude", 0.0)
                })
            plans[day_key] = {"schedule": schedule_list}
    else:
        raise ValueError("plans 필드가 예상한 형식이 아닙니다.")

    return {
        "aiEmpathy": response_json.get("aiEmpathy", ""),
        "tags": response_json.get("tags", []),
        "plans": plans
    }



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
    # 감정 → 스타일 매핑은 향후 활용 가능
    styles = map_emotions_to_styles(emotions)

    # GPT용 프롬프트 생성
    prompt = generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions, peopleCount)

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful travel itinerary planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    full_text = response.choices[0].message.content
    print("GPT 응답 내용:\n", full_text)

    # JSON 파싱 및 형식 정규화
    schedule_json = extract_json_from_ai_response(full_text)
    schedule_formatted = normalize_schedule_format(schedule_json)

    # Pydantic 모델로 변환
    return ScheduleAIResponse(**schedule_formatted)


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
        # 오류 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=str(e))
