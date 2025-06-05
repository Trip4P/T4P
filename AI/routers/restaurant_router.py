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
    meals_json = json.dumps(meals_data, ensure_ascii=False)
    return f'''
당신은 사용자 맞춤형 맛집 추천 AI입니다.

조건:
- 응답은 반드시 JSON 형식으로만 출력하세요.
- 마크다운, 설명 문장, 안내 문구는 절대 포함하지 마세요.
- JSON은 중괄호 {{}}로 감싸고, 모든 key는 큰따옴표 "로 감싸야 합니다.
- 사용자 조건을 기반으로 아래 맛집 리스트 중 **정확히 4~5개**만 선택하세요.

[사용자 조건]
도시: {data.city}
지역: {data.region}
선호 음식: {", ".join(data.foodPreference)}
분위기: {", ".join(data.atmospheres)}
동행자: {", ".join(data.companion)}

[맛집 리스트]
{meals_json}

[응답 예시]
{{
  "aiComment": "추천 요약 코멘트",
  "places": [
    {{
      "name": "맛집 이름",
      "aiFoodComment": "해당 음식에 대한 짧은 설명",
      "tags": ["데이트", "가성비"],
      "placeId": "ChIJxxxxxx",
      "imageUrl": "https://example.com/image.jpg"
    }}
  ]
}}
'''

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
            max_tokens=3000
        )

        content = response.choices[0].message.content.strip()
        print("GPT raw response:\n", content)  # 디버깅 출력

        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        parsed_json = content[json_start:json_end]
        return json.loads(parsed_json)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="GPT 응답이 JSON 형식이 아닙니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 오류: {str(e)}")
