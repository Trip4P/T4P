from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db  # 동기 세션 의존성 주입
from pydantic import BaseModel
from typing import List, Optional
from models import Meal  # ORM 모델 임포트 (경로에 맞게 수정)

router = APIRouter(prefix="/api")

class ReviewHighlight(BaseModel):
    #title: Optional[str] = None
    date: str
    review: str

class Location(BaseModel):
    lat: str
    lon: str

class PlaceDetail(BaseModel):
    image: str
    place: str
    tags: List[str]
    businessHours: str
    price: str
    address: str
    phone: str
    averageRate: str
    reviewCount: str
    aiComment: str
    reviewHighlights: Optional[ReviewHighlight]
    satisfaction: str
    reviewKeywords: List[str]
    location: Location
price_map = {
    0: 0,
    1: 7000,
    2: 14000,
    3: 23000,
    4: 40000
}

@router.get("/food-places-detail/{place_id}", response_model=PlaceDetail)
def get_place_detail(place_id: str, db: Session = Depends(get_db)):
    print(f"Received request for place_id: {place_id}")  # 요청 들어오는지 확인

    meal = db.query(Meal).filter(Meal.place_id == place_id).first()
    if not meal:
        print(f"Place not found for place_id: {place_id}")  # place_id DB 조회 결과 없을 때
        raise HTTPException(status_code=404, detail="Place not found")

    review_result = db.execute(
        text("SELECT created_at, comment FROM reviews WHERE meal_id = :mid ORDER BY created_at DESC LIMIT 1"),
        {"mid": meal.id}
    )
    review = review_result.fetchone()

    review_data = None
    if review:
        review_data = ReviewHighlight(
            date=review.created_at.strftime("%Y.%m.%d"),
            review=review.comment,
        )

    price_val = price_map.get(meal.price_level, 0)
    price_str = f"인당 약 {price_val:,}원" if price_val > 0 else "가격 정보 없음"

    print(f"Returning data for place_id: {place_id}, meal.name: {meal.name}")  # 응답 직전 로그

    return PlaceDetail(
        image=meal.image_url,
        place=meal.name,
        tags=meal.food_type.split(",") if meal.food_type else [],
        businessHours=meal.opening_hours or "",
        price=price_str,
        address=meal.location or "",
        phone=meal.phone_number or "",
        averageRate=str(meal.rating or 0),
        reviewCount=str(meal.review_count or 0),
        aiComment="",
        reviewHighlights=review_data,
        satisfaction=str(int((meal.rating or 0) * 20)),
        reviewKeywords = meal.keywords if meal.keywords else [],
        location=Location(lat=str(meal.latitude or 0), lon=str(meal.longitude or 0))
    )
