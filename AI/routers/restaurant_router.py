from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from config import settings
from database import get_db
import json

router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 요청 모델
class RestaurantRequest(BaseModel):
    companion: List[str]
    foodPreference: List[str]
    atmospheres: List[str]
    city: str
    region: str

# 응답 모델
class RestaurantPlace(BaseModel):
    name: str
    aiFoodComment: str
    tags: List[str]
    placeId: str
    imageUrl: str

class RestaurantResponse(BaseModel):
    aiComment: str
    places: List[RestaurantPlace]

# DB에서 meals 테이블 쿼리
def fetch_meals_from_db(db: Session, city: str, region: str):
    results = db.execute(text("""
        SELECT place_id, name, food_type, image_url,
               rating, review_count, price_level,
               style_quiet, style_date, style_family,
               style_view, style_modern, style_traditional
        FROM meals
        WHERE location ILIKE :region AND location ILIKE :city
        LIMIT 50
    """), {"region": f"%{region}%", "city": f"%{city}%"}).fetchall()

    style_map = {
        "style_quiet": "조용한",
        "style_date": "데이트",
        "style_family": "가족모임",
        "style_view": "뷰 맛집",
        "style_modern": "모던한",
        "style_traditional": "전통적인"
    }

    def row_to_dict(r):
        row = dict(r._mapping)
        tags = [label for key, label in style_map.items() if row.get(key)]
        return {
            "placeId": str(row["place_id"]),
            "name": row["name"],
            "food_type": row["food_type"],
            "imageUrl": row["image_url"],
            "rating": float(row["rating"]) if row["rating"] else None,
            "reviewCount": row["review_count"],
            "priceLevel": row["price_level"],
            "tags": tags
        }

    return [row_to_dict(r) for r in results]

# GPT 프롬프트 생성
def generate_prompt(data: RestaurantRequest, meals_data: List[dict]) -> str:
    meals_json = json.dumps(meals_data, ensure_ascii=False, indent=2)
    return f"""
당신은 사용자 맞춤형 여행 맛집 추천 전문가입니다.
아래 조건에 따라 반드시 중괄호로 시작하고 끝나는 JSON 형식으로만 응답하십시오.
설명, 해석, 마크다운 등은 절대 포함하지 마십시오.

사용자 정보:
- 여행지: {data.city} {data.region}
- 선호 음식: {", ".join(data.foodPreference)}
- 선호 분위기: {", ".join(data.atmospheres)}
- 동행자: {", ".join(data.companion)}

추천 조건:
- meals 데이터 안에서만 선택하여 정확히 4개에서 5개의 맛집을 추천하십시오.
- 음식 종류, 분위기, 동행자 조건에 가장 잘 부합하는 장소를 우선 추천하십시오.
- 응답에는 반드시 aiFoodComment, tags, placeId, imageUrl 항목이 포함되어야 합니다.

meals 데이터:
{meals_json}

응답 예시:
{{
  "aiComment": "서울 강남에서 가족과 함께하기 좋은 맛집들을 엄선했어요.",
  "places": [
    {{
      "name": "맛집 이름",
      "aiFoodComment": "음식에 대한 간단한 설명",
      "tags": ["데이트", "가족모임"],
      "placeId": "ChIJxxxxxx",
      "imageUrl": "https://example.com/image.jpg"
    }}
  ]
}}
"""

# 라우터 엔드포인트
@router.post("/ai/restaurant", response_model=RestaurantResponse)
async def ai_recommend_restaurant(data: RestaurantRequest, db: Session = Depends(get_db)):
    meals = fetch_meals_from_db(db, data.city, data.region)
    if not meals:
        raise HTTPException(status_code=404, detail="해당 지역 맛집 정보가 없습니다.")

    prompt = generate_prompt(data, meals)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "넌 사용자 맞춤 맛집 추천 AI야. 반드시 JSON 형식으로 응답해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )

        content = response.choices[0].message.content.strip()
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        parsed_json = content[json_start:json_end]
        return json.loads(parsed_json)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="GPT 응답이 JSON 형식이 아닙니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 오류: {str(e)}")
