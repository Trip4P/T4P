from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db  
from pydantic import BaseModel
from typing import List, Optional
from models import Meal, Review
import json
import openai
from dotenv import load_dotenv
import os
import asyncio

router = APIRouter(prefix="/api")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 요청 모델
class FoodPlaceRequest(BaseModel):
    placeId: str
    companions: List[str]
    atmospheres: List[str]

# 응답 관련 모델
class ReviewHighlight(BaseModel):
    date: str
    review: str

class Location(BaseModel):
    lat: Optional[str]
    lon: Optional[str]

class PlaceDetail(BaseModel):
    image: Optional[str]
    place: Optional[str]
    tags: List[str]
    businessHours: Optional[str]
    price: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    averageRate: Optional[str]
    reviewCount: Optional[str]
    aiComment: Optional[str]
    reviewHighlights: Optional[ReviewHighlight]
    satisfaction: Optional[str]
    reviewKeywords: List[str]
    location: Location
    placeType: str = "meal"

price_map = {
    0: 0,
    1: 7000,
    2: 14000,
    3: 23000,
    4: 40000
}

def parse_keywords(raw_keywords):
    if not raw_keywords:
        return []
    if isinstance(raw_keywords, list):
        return raw_keywords
    try:
        return json.loads(raw_keywords)
    except Exception:
        return raw_keywords.split(",")

# AI 코멘트 생성 함수
def generate_ai_comment_from_reviews(place_name: str, reviews: List[str], companions: List[str], atmospheres: List[str]) -> str:
    review_text = " ".join(reviews)
    
    prompt = f"""
    {place_name}에 대해 아래와 같은 분위기를 가진 장소라고 생각해보세요: {', '.join(atmospheres)}.
    사용자는 {', '.join(companions)}과 함께 방문하려고 합니다.
    
    다음은 이 장소에 대한 실제 리뷰들입니다:
    {review_text}
    
    위 정보를 바탕으로 감성적이고 따뜻한 추천 메시지를 2~3문장으로 작성해주세요.
    - 동반자 유형에 맞는 활동/분위기를 간결하게 설명
    - 이모지를 적절히 활용 (예: 🌿, 🍽️, 👨‍👩‍👧‍👦)
    - 리뷰 내용은 요약해서 반영, 직접 인용 금지
    - 부정적인 내용은 제외
    - 리뷰가 없는 경우에는 내용을 만들어내지 말고, 대신 사용자가 선택한 분위기나 동반자 정보를 기반으로 따뜻하고 공감 가는 추천 문장을 작성해주세요.
    """
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "당신은 감성적인 맛집 추천 전문가입니다. 사용자 리뷰를 바탕으로 간결하고 따뜻한 문장을 작성하세요."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.8,
        )
        return completion.choices[0].message.content.strip()
    except asyncio.CancelledError:
        raise
    except Exception:
        return "추천 사유를 생성하는 데 문제가 발생했습니다."

def fetch_random_review(db: Session, meal_id: int) -> Optional[ReviewHighlight]:
    result = db.execute(
        text("SELECT created_at, comment FROM reviews WHERE meal_id = :id ORDER BY RANDOM() LIMIT 1"),
        {"id": meal_id}
    ).fetchone()
    if result:
        return ReviewHighlight(
            date=result.created_at.strftime("%Y.%m.%d"),
            review=result.comment
        )
    return None

def fetch_reviews_for_meal(db: Session, meal_id: int) -> List[str]:
    reviews = db.query(Review).filter(Review.meal_id == meal_id).all()
    return [r.comment for r in reviews]

@router.post("/food-places-detail", response_model=PlaceDetail)
async def get_meal_detail(request: FoodPlaceRequest, db: Session = Depends(get_db)):
    place_id = request.placeId
    companions = request.companions
    atmospheres = request.atmospheres

    # meal 데이터 조회
    meal = db.query(Meal).filter(Meal.place_id == place_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Place not found")


    reviews = fetch_reviews_for_meal(db, meal.id)
    ai_comment = await asyncio.to_thread(generate_ai_comment_from_reviews, meal.name, reviews, companions, atmospheres)

    review_data = fetch_random_review(db, meal.id) #리뷰랜덤으로 선정

    # 가격 문자열
    price_val = price_map.get(meal.price_level)
    price_str = f"인당 약 {price_val:,}원" if price_val else "가격 정보 없음"

    return PlaceDetail(
        image=meal.image_url,
        place=meal.name,
        tags=meal.food_type.split(",") if meal.food_type else [],
        businessHours=meal.opening_hours,
        price=price_str,
        address=meal.location,
        phone=meal.phone_number,
        averageRate=str(meal.rating) if meal.rating is not None else None,
        reviewCount=str(meal.review_count) if meal.review_count is not None else None,
        aiComment=ai_comment,
        reviewHighlights=review_data,
        satisfaction=str(int(meal.rating * 20)) if meal.rating is not None else None,
        reviewKeywords=parse_keywords(meal.keywords) if hasattr(meal, 'keywords') else [],
        location=Location(
            lat=str(meal.latitude) if meal.latitude is not None else None,
            lon=str(meal.longitude) if meal.longitude is not None else None
        ),
        placeType="meal"
    )
