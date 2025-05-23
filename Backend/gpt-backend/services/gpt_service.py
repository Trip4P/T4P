import re
import json
from openai import OpenAI
from config import settings

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions):
    emotion_str = ", ".join(emotions)
    companions_str = ", ".join(companions)
    return (
        f"출발지: {start_city}\n"
        f"도착지: {end_city}\n"
        f"여행 기간: {start_date}부터 {end_date}까지\n"
        f"사용자 감정: {emotion_str}\n"
        f"동행인: {companions_str}\n"
        "이 정보로 사용자에게 맞춤형 여행 일정을 추천해줘.\n"
        "결과는 JSON 형식으로 예시와 함께 줘."
    )

def extract_json_from_ai_response(ai_response_text):
    """
    AI 응답 텍스트에서 ```json ... ``` 코드블록 안의 JSON 문자열을 추출하여 dict로 반환.
    """
    pattern = r"```json(.*?)```"
    match = re.search(pattern, ai_response_text, re.DOTALL)
    if not match:
        raise ValueError("AI 응답에 JSON 코드블록이 없습니다.")
    json_str = match.group(1).strip()
    return json.loads(json_str)

def get_ai_schedule(start_city, end_city, start_date, end_date, emotions, companions):
    prompt = generate_schedule_prompt(start_city, end_city, start_date, end_date, emotions, companions)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful travel itinerary planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    full_text = response.choices[0].message.content

    try:
        schedule_json = extract_json_from_ai_response(full_text)
    except Exception as e:
        raise RuntimeError(f"AI 응답 JSON 파싱 실패: {e}")

    # dict -> JSON 문자열로 변환해서 리턴
    return json.dumps(schedule_json, ensure_ascii=False)


# 예시 실행 (테스트용)
if __name__ == "__main__":
    start_city = "서울"
    end_city = "부산"
    start_date = "2025-06-01"
    end_date = "2025-06-03"
    emotions = ["힐링", "자연"]
    companions = ["친구"]

    schedule = get_ai_schedule(start_city, end_city, start_date, end_date, emotions, companions)
    print(json.dumps(schedule, ensure_ascii=False, indent=2))
