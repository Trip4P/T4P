from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from services.recommend_service import recommend_restaurants
from database import get_db

router = APIRouter()

class RestaurantRequest(BaseModel):
    user_id: int
    companion: List[str]
    food_types: List[str]
    mood: List[str]
    city: str
    region: str
    styles: List[str] = []  # ✅ 이거 빠지면 오류남!

@router.post("/recommend/restaurant")
def get_restaurant_recommendation(
    request: RestaurantRequest,
    db: Session = Depends(get_db)
):
    try:
        result = recommend_restaurants(request, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
