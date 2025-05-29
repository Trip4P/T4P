import re
import json
from openai import OpenAI
from config import settings
from sqlalchemy import text
from sqlalchemy.orm import Session

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 감정 → 스타일 매핑
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

def map_emotions_to_styles(emotions):
    styles = set()
    for emo in emotions:
        styles.update(EMOTION_TO_STYLE.get(emo, []))
    return list(styles)

def generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions):
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)
    return (
        f"출발지: {start_city}\n"
        f"도착지: {end_city}\n"
        f"여행 기간: {start_date}부터 {end_date}까지\n"
        f"사용자 감정: {emotion_str}\n"
        f"동행인: {companions_str}\n\n"
        "이 정보를 기반으로 사용자에게 맞춤형 여행 일정을 추천해줘.\n"
        "각 날짜(day1, day2, ...) 별로 관광지(sights) 및 점심(lunch), 저녁(dinner)을 반드시 포함하되, "
        "값이 없으면 빈 리스트([])로 표시해줘.\n\n"
        "아래 예시처럼 반드시 정확한 JSON 형식으로 코드블록만 출력해야 하며, "
        "중복 키나 문법 오류가 없도록 해주세요.\n\n"
        "예시:\n"
        "```json\n"
        "{\n"
        "  \"day1\": {\n"
        "    \"sights\": [\n"
        "      {\"name\": \"명소1\", \"place_id\": \"abcd1234\"}\n"
        "    ],\n"
        "    \"lunch\": [\n"
        "      {\"name\": \"식당1\", \"place_id\": \"efgh5678\"}\n"
        "    ],\n"
        "    \"dinner\": []\n"
        "  },\n"
        "  \"day2\": {\n"
        "    \"sights\": [],\n"
        "    \"lunch\": [],\n"
        "    \"dinner\": []\n"
        "  }\n"
        "}\n"
        "```\n"
        "이 형식을 꼭 지켜서 JSON 코드블록만 응답해줘."
        "반드시 올바른 JSON 형식의 코드블록만 출력하고, 중복 키나 문법 오류가 없도록 해주세요."
    )

def extract_json_from_ai_response(ai_response_text):
    # AI 응답에서 ```json ... ``` 코드블록 안의 JSON 추출
    pattern = r"```json\s*(.*?)```"
    match = re.search(pattern, ai_response_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # 코드블록 없으면 전체 텍스트 시도
        json_str = ai_response_text.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n원본: {json_str}")

def normalize_schedule_format(schedule):
    """
    AI가 반환한 스케줄이
    - dayN: list (잘못된 경우)면 -> dayN: {sights: [], lunch: [], dinner: []}
    - dayN: dict 인 경우 누락된 키 보완
    """
    for day_key, day_value in list(schedule.items()):
        if isinstance(day_value, list):
            # 리스트면, 빈 dict로 바꾸고, 리스트에 실제 장소가 있으면 sights로 넣기
            normalized = {"sights": [], "lunch": [], "dinner": []}
            for item in day_value:
                if isinstance(item, dict) and "name" in item and "place_id" in item:
                    normalized["sights"].append({
                        "name": item["name"],
                        "place_id": item.get("place_id", "")
                    })
            schedule[day_key] = normalized
        elif isinstance(day_value, dict):
            # dict일 때 각 카테고리가 리스트인지 체크, 아니면 빈 리스트로 보완
            for category in ["sights", "lunch", "dinner"]:
                if category not in day_value or not isinstance(day_value[category], list):
                    day_value[category] = []
                else:
                    filtered = []
                    for place in day_value[category]:
                        if isinstance(place, dict) and "name" in place and "place_id" in place:
                            filtered.append({
                                "name": place["name"],
                                "place_id": place.get("place_id", "")
                            })
                    day_value[category] = filtered
        else:
            # dict/list 둘 다 아니면 빈 구조로 초기화
            schedule[day_key] = {"sights": [], "lunch": [], "dinner": []}

    return schedule

def recommend_restaurants(db: Session, food_types, region):
    sql = text("""
        SELECT name, food_type, area, rating, review_count, image_url, place_id
        FROM meals
        WHERE food_type = ANY(:food_types)
          AND area ILIKE :region
        ORDER BY rating DESC
        LIMIT 20;
    """)
    result = db.execute(sql, {"food_types": food_types, "region": f"%{region}%"}).fetchall()
    return [dict(row) for row in result]

def distribute_restaurants_to_days(schedule):
    """
    schedule에서 "restaurants" 키가 있으면 각 day의 lunch/dinner에 균등 분배
    description 없이 name, place_id만 사용
    """
    restaurants = schedule.pop("restaurants", [])
    day_keys = sorted(schedule.keys())
    num_days = len(day_keys)
    if num_days == 0 or not restaurants:
        return

    # 각 day가 dict형태인지 확인 및 기본값 보장
    for day in day_keys:
        if not isinstance(schedule[day], dict):
            schedule[day] = {"sights": [], "lunch": [], "dinner": []}
        for category in ["sights", "lunch", "dinner"]:
            if category not in schedule[day] or not isinstance(schedule[day][category], list):
                schedule[day][category] = []

    total_meals = len(restaurants)
    meals_per_day = (total_meals // (num_days * 2)) * 2
    if meals_per_day == 0 and total_meals > 0:
        meals_per_day = min(2, total_meals)  # 최소 하루 2개는 배분

    idx = 0
    for day in day_keys:
        lunch_count = dinner_count = meals_per_day // 2
        lunch_places = restaurants[idx: idx + lunch_count]
        idx += lunch_count
        dinner_places = restaurants[idx: idx + dinner_count]
        idx += dinner_count

        schedule[day]["lunch"] = [{"name": r["name"], "place_id": r.get("place_id", "")} for r in lunch_places]
        schedule[day]["dinner"] = [{"name": r["name"], "place_id": r.get("place_id", "")} for r in dinner_places]

    # 남은 음식점 있으면 점심에 추가 분배
    while idx < total_meals:
        for day in day_keys:
            if idx >= total_meals:
                break
            schedule[day]["lunch"].append({
                "name": restaurants[idx]["name"],
                "place_id": restaurants[idx].get("place_id", "")
            })
            idx += 1

def get_ai_schedule(db: Session, start_city, end_city, start_date, end_date, emotions, companions, food_types, region):
    styles = map_emotions_to_styles(emotions)  # 필요시 프롬프트 반영 가능

    prompt = generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful travel itinerary planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7,
    )

    full_text = response.choices[0].message.content
    print("GPT 응답 내용:\n", full_text)

    # AI 응답에서 JSON 추출 및 파싱
    schedule_json = extract_json_from_ai_response(full_text)

    # AI 응답 일정 구조 정규화
    schedule_json = normalize_schedule_format(schedule_json)

    # DB에서 음식점 추천
    restaurants = recommend_restaurants(db, food_types, region)
    schedule_json["restaurants"] = restaurants

    # 음식점 분배
    distribute_restaurants_to_days(schedule_json)

    return schedule_json


# 테스트용 실행 코드
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    start_city = "서울"
    end_city = "부산"
    start_date = "2025-06-01"
    end_date = "2025-06-03"
    emotions = ["기쁜", "힐링"]
    companions = ["친구"]
    food_types = ["한식", "카페"]
    region = "부산"

    schedule = get_ai_schedule(
        db, start_city, end_city, start_date, end_date,
        emotions, companions, food_types, region
    )

    import pprint
    pprint.pprint(schedule)
