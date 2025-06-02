from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel
from typing import List, Optional
from models import Meal, Destination 
import json 

router = APIRouter(prefix="/api")

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
    placeType: str  # 추가

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
        # 이미 리스트면 그대로 반환
        return raw_keywords
    try:
        return json.loads(raw_keywords)
    except Exception as e:
        print(f"[WARN] Failed to parse keywords as JSON: {e}")
        return raw_keywords.split(",")  # fallback

@router.get("/places-detail/{place_id}", response_model=PlaceDetail)
def get_place_detail(place_id: str, db: Session = Depends(get_db)):
    print(f"[DEBUG] Received place_id: {place_id}")

    # meal 먼저 조회
    meal = db.query(Meal).filter(Meal.place_id == place_id).first()
    print(f"[DEBUG] Meal found: {meal}")

    if meal is None:
        print("[DEBUG] No meal found, trying destination...")
        dest = db.query(Destination).filter(Destination.place_id == place_id).first()
        print(f"[DEBUG] Destination found: {dest}")

        if dest is None:
            print("[ERROR] No place found in meals or destinations.")
            raise HTTPException(status_code=404, detail="Place not found")

        # destination 리뷰 조회
        review_result = db.execute(
            text("SELECT created_at, comment FROM reviews WHERE destination_id = :did ORDER BY created_at DESC LIMIT 1"),
            {"did": dest.id}
        )
        review = review_result.fetchone()
        print(f"[DEBUG] Destination review fetched: {review}")

        review_data = None
        if review:
            review_data = ReviewHighlight(
                date=review.created_at.strftime("%Y.%m.%d"),
                review=review.comment,
            )

        price_val = price_map.get(dest.price_level, None)
        price_str = f"인당 약 {price_val:,}원" if price_val else None

        print(f"[DEBUG] Returning destination data for place_id: {place_id}")
        return PlaceDetail(
            image=dest.image_url or None,
            place=dest.name or None,
            tags=[],  # 빈 리스트
            businessHours=dest.opening_hours or None,
            price=price_str,
            address=dest.location or None,
            phone=dest.phone_number or None,
            averageRate=str(dest.rating) if dest.rating is not None else None,
            reviewCount=str(dest.review_count) if dest.review_count is not None else None,
            aiComment=None,
            reviewHighlights=review_data,
            satisfaction=str(int(dest.rating * 20)) if dest.rating is not None else None,
            reviewKeywords=parse_keywords(dest.keywords),
            location=Location(
                lat=str(dest.latitude) if dest.latitude is not None else None,
                lon=str(dest.longitude) if dest.longitude is not None else None
            ),
            placeType="destination"
        )

    # meal 있을 때 리뷰 조회
    review_result = db.execute(
        text("SELECT created_at, comment FROM reviews WHERE meal_id = :mid ORDER BY created_at DESC LIMIT 1"),
        {"mid": meal.id}
    )
    review = review_result.fetchone()
    print(f"[DEBUG] Meal review fetched: {review}")

    review_data = None
    if review:
        review_data = ReviewHighlight(
            date=review.created_at.strftime("%Y.%m.%d"),
            review=review.comment,
        )

    price_val = price_map.get(meal.price_level, None)
    price_str = f"인당 약 {price_val:,}원" if price_val else None

    print(f"[DEBUG] Returning meal data for place_id: {place_id}, meal.name: {meal.name}")

    return PlaceDetail(
        image=meal.image_url or None,
        place=meal.name or None,
        tags=meal.food_type.split(",") if meal.food_type else [],
        businessHours=meal.opening_hours or None,
        price=price_str,
        address=meal.location or None,
        phone=meal.phone_number or None,
        averageRate=str(meal.rating) if meal.rating is not None else None,
        reviewCount=str(meal.review_count) if meal.review_count is not None else None,
        aiComment=None,
        reviewHighlights=review_data,
        satisfaction=str(int(meal.rating * 20)) if meal.rating is not None else None,
        reviewKeywords=parse_keywords(meal.keywords),
        location=Location(
            lat=str(meal.latitude) if meal.latitude is not None else None,
            lon=str(meal.longitude) if meal.longitude is not None else None
        ),
        placeType="meal"
    )
