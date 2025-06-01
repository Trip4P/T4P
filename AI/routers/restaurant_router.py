from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import openai
import os
import json

router = APIRouter()

# Request Body 모델
class RestaurantRequest(BaseModel):
    companion: List[str]
    foodPreference: List[str]
    atmospheres: List[str]
    city: str
    region: str

# Response 모델
class RestaurantPlace(BaseModel):
    name: str
    aiFoodComment: str
    tags: List[str]
    placeId: int

class RestaurantResponse(BaseModel):
    aiComment: str
    places: List[RestaurantPlace]

# GPT Prompt 생성 함수
def generate_prompt(data: RestaurantRequest) -> str:
    return f"""
사용자가 '{data.city} {data.region}' 지역으로 여행을 갑니다.
이 사람은 {", ".join(data.foodPreference)}을 좋아하고,
{", ".join(data.atmospheres)} 같은 분위기를 선호하며,
{", ".join(data.companion)} 함께 여행하고 있습니다.

이 조건을 바탕으로 해당 지역에서 어울리는 맛집 2~3곳을 JSON 형식으로 추천해주세요.

응답은 아래 형식의 JSON으로 출력해줘:

{{
  "aiComment": "한 줄 요약 코멘트",
  "places": [
    {{
      "name": "맛집 이름",
      "aiFoodComment": "AI가 음식에 대해 한 줄 설명",
      "tags": ["뷰맛집", "가성비", ...],
      "placeId": 숫자 (임의 번호 부여)
    }}
  ]
}}
    """

@router.post("/ai/restaurant", response_model=RestaurantResponse)
async def ai_recommend_restaurant(data: RestaurantRequest):
    prompt = generate_prompt(data)

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "넌 여행 맛집 추천 전문가야. JSON 형식으로 정확히 응답해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="GPT 응답이 JSON 형식이 아닙니다.")

        return parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 오류: {e}")
