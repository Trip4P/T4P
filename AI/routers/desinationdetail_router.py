from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel
from typing import List, Optional
from models import Meal, Destination, Accommodation, Review
import json
import openai
from dotenv import load_dotenv
import os
import asyncio

router = APIRouter(prefix="/api")

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 캐시 딕셔너리
ai_comment_cache = {}

# AI comment generation
async def get_ai_comment_cached(place_name: str, reviews: List[str], emotions: List[str], companions: List[str], people_count: int) -> str:
    key = f"{place_name}-{','.join(emotions)}-{','.join(companions)}-{people_count}"
    if key in ai_comment_cache:
        return ai_comment_cache[key]

    review_text = " ".join(reviews)
    prompt = f"""
    {place_name}에 대해 {emotions} 감정을 가진 {companions}와 함께 {people_count}명이 여행을 간다고 상상해보세요.
    아래는 이 여행지에 대한 리뷰입니다: 
    {review_text}
    
    이 정보를 바탕으로, 감정과 사람들과 어울릴 수 있는 여행 활동이나 경험을 추천해주세요.
    특히, 추천을 할 때에는 감정적으로 공감할 수 있는 말을 해주시고, 활동 추천에 이모지를 적절히 활용해주세요.
    부정적인 이야기는 피해주세요. 
    리뷰가 없는 경우에는 내용을 만들어내지 말고, 대신 사용자가 선택한 분위기나 동반자 정보를 기반으로 따뜻하고 공감 가는 추천 문장을 작성해주세요.
    여행지를 잘 모르는 사람에게, "혼자 여행하는 사람", "가족과 함께 가는 사람", "친구와 함께 가는 사람" 등으로 구체적인 상황을 상상하면서 추천해주세요.
    예: "이곳은 여유롭게 혼자만의 시간을 보낼 수 있는 곳이에요 🌿", "친구들과 함께 와서 즐길 수 있는 활기찬 장소예요 🕺", "가족과 함께 가기 좋은 편안한 분위기의 여행지입니다 👨‍👩‍👧"
    """
    try:
        completion = await asyncio.to_thread(openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "당신은 여행 추천 전문가입니다. 사용자의 감정과 동반자 정보를 바탕으로 창의적이고 유용한 추천 사유를 작성하세요. 단, 문장은 2~4문장 정도로 간결하게 작성하고, 리뷰를 직접적으로 나열하지 마세요."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.8,
        )
        ai_comment = completion.choices[0].message.content.strip()
        ai_comment_cache[key] = ai_comment
        return ai_comment
    except asyncio.CancelledError:
        raise
    except Exception:
        return "추천 사유를 생성하는 데 문제가 발생했습니다."

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
    placeType: str

class PlaceRequest(BaseModel):
    placeId: str
    emotions: List[str]
    companions: List[str]
    peopleCount: int

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

def fetch_reviews_for_ai(db: Session, place_id: str, place_type: str):
    reviews = []
    if place_type == "meal":
        meal = db.query(Meal).filter(Meal.place_id == place_id).first()
        if meal:
            reviews = db.query(Review).filter(Review.meal_id == meal.id).all()
    elif place_type == "destination":
        destination = db.query(Destination).filter(Destination.place_id == place_id).first()
        if destination:
            reviews = db.query(Review).filter(Review.destination_id == destination.id).all()
    elif place_type == "accommodation":
        accommodation = db.query(Accommodation).filter(Accommodation.place_id == place_id).first()
        if accommodation:
            reviews = db.query(Review).filter(Review.accommodation_id == accommodation.id).all()
    return [review.comment for review in reviews]

def fetch_random_review(db: Session, column_name: str, id_value: int):
    query = text(f"SELECT created_at, comment FROM reviews WHERE {column_name} = :id ORDER BY RANDOM() LIMIT 1")
    result = db.execute(query, {"id": id_value}).fetchone()
    if result:
        return ReviewHighlight(date=result.created_at.strftime("%Y.%m.%d"), review=result.comment)
    return None

@router.post("/places-detail", response_model=PlaceDetail)
async def get_place_detail(place_request: PlaceRequest, db: Session = Depends(get_db)):
    place_id = place_request.placeId
    emotions = place_request.emotions
    companions = place_request.companions
    people_count = place_request.peopleCount

    meal = db.query(Meal).filter(Meal.place_id == place_id).first()
    if meal:
        reviews_task = asyncio.to_thread(fetch_reviews_for_ai, db, place_id, "meal")
        review_data_task = asyncio.to_thread(fetch_random_review, db, "meal_id", meal.id)
        reviews, review_data = await asyncio.gather(reviews_task, review_data_task)
        ai_comment = await get_ai_comment_cached(meal.name, reviews, emotions, companions, people_count)
        price_val = price_map.get(meal.price_level)
        return PlaceDetail(
            image=meal.image_url,
            place=meal.name,
            tags=meal.food_type.split(",") if meal.food_type else [],
            businessHours=meal.opening_hours,
            price=f"인당 약 {price_val:,}원" if price_val else None,
            address=meal.location,
            phone=meal.phone_number,
            averageRate=str(meal.rating) if meal.rating is not None else None,
            reviewCount=str(meal.review_count) if meal.review_count is not None else None,
            aiComment=ai_comment,
            reviewHighlights=review_data,
            satisfaction=str(int(meal.rating * 20)) if meal.rating is not None else None,
            reviewKeywords=parse_keywords(meal.keywords) if hasattr(meal, 'keywords') else [],
            location=Location(lat=str(meal.latitude) if meal.latitude is not None else None, lon=str(meal.longitude) if meal.longitude is not None else None),
            placeType="meal"
        )

    dest = db.query(Destination).filter(Destination.place_id == place_id).first()
    if dest:
        reviews_task = asyncio.to_thread(fetch_reviews_for_ai, db, place_id, "destination")
        review_data_task = asyncio.to_thread(fetch_random_review, db, "destination_id", dest.id)
        reviews, review_data = await asyncio.gather(reviews_task, review_data_task)
        ai_comment = await get_ai_comment_cached(dest.name, reviews, emotions, companions, people_count)
        price_val = price_map.get(dest.price_level)
        return PlaceDetail(
            image=dest.image_url,
            place=dest.name,
            tags=[],
            businessHours=dest.opening_hours,
            price=f"인당 약 {price_val:,}원" if price_val else None,
            address=dest.location,
            phone=dest.phone_number,
            averageRate=str(dest.rating) if dest.rating is not None else None,
            reviewCount=str(dest.review_count) if dest.review_count is not None else None,
            aiComment=ai_comment,
            reviewHighlights=review_data,
            satisfaction=str(int(dest.rating * 20)) if dest.rating is not None else None,
            reviewKeywords=parse_keywords(dest.keywords) if hasattr(dest, 'keywords') else [],
            location=Location(lat=str(dest.latitude) if dest.latitude is not None else None, lon=str(dest.longitude) if dest.longitude is not None else None),
            placeType="destination"
        )

    accom = db.query(Accommodation).filter(Accommodation.place_id == place_id).first()
    if accom:
        reviews_task = asyncio.to_thread(fetch_reviews_for_ai, db, place_id, "accommodation")
        review_data_task = asyncio.to_thread(fetch_random_review, db, "accommodation_id", accom.id)
        reviews, review_data = await asyncio.gather(reviews_task, review_data_task)
        ai_comment = await get_ai_comment_cached(accom.name, reviews, emotions, companions, people_count)
        return PlaceDetail(
            image=accom.image_url,
            place=accom.name,
            tags=accom.category.split(",") if accom.category else [],
            businessHours=accom.opening_hours,
            price=f"1박당 약 {accom.price:,}원" if accom.price else "가격 정보 없음",
            address=accom.location,
            phone=accom.phone_number,
            averageRate=str(accom.rating) if accom.rating is not None else None,
            reviewCount=str(accom.review_count) if accom.review_count is not None else None,
            aiComment=ai_comment,
            reviewHighlights=review_data,
            satisfaction=str(int(accom.rating * 20)) if accom.rating is not None else None,
            reviewKeywords=parse_keywords(accom.keywords) if hasattr(accom, 'keywords') else [],
            location=Location(lat=str(accom.latitude) if accom.latitude is not None else None, lon=str(accom.longitude) if accom.longitude is not None else None),
            placeType="accommodation"
        )

    raise HTTPException(status_code=404, detail="Place not found")