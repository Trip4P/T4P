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
        f"동행인: {companions_str}\n\n"
        "이 정보를 기반으로 사용자에게 맞춤형 여행 일정을 추천해줘.\n"
        "각 날짜별로 추천 장소를 JSON 형식으로 반환해줘. 각 장소는 다음 필드를 가져야 해:\n"
        "- name: 장소 이름\n"
        "- place_id: Google Maps Place ID (가능한 정확히 추정)\n"
        "- description: 간단한 설명 (선택사항)\n\n"
        "✅ 반드시 아래와 같은 형태로 JSON 코드블록만 응답해줘.\n"
        "예시:\n"
        "```json\n"
        "{\n"
        "  \"day1\": [\n"
        "    {\"name\": \"해운대 해수욕장\", \"place_id\": \"ChIJcQDBn9yRfDURJ9NwYf-VS9M\"},\n"
        "    {\"name\": \"광안리 해변\", \"place_id\": \"ChIJK_-T5N5RfDURToKzG1jH58g\"}\n"
        "  ],\n"
        "  \"day2\": [ ... ]\n"
        "}\n"
        "```"
    )



def extract_json_from_ai_response(ai_response_text):
    """
    GPT 응답에서 ```json ... ``` 코드블록 또는 순수 JSON 문자열을 파싱
    """
    # 코드블럭 안 JSON 추출 시도
    pattern = r"```json(.*?)```"
    match = re.search(pattern, ai_response_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # 코드블럭이 없으면 전체 응답을 그대로 시도
        json_str = ai_response_text.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}")


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

    # 디버깅용 출력
    print("GPT 응답 내용:\n", full_text)

    try:
        schedule_json = extract_json_from_ai_response(full_text)
    except Exception as e:
        raise RuntimeError(f"AI 응답 JSON 파싱 실패: {e}")

    return schedule_json  # dict 그대로 반환

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
