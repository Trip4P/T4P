from fastapi import APIRouter, Depends
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List

router = APIRouter()

class RecommendRequest(BaseModel):
    user_id: int
    companion: List[str]
    food_types: List[str]
    mood: List[str]
    city: str
    region: str
    styles: List[str] = []

def recommend_restaurants(request: RecommendRequest, db: Session):
    style_conditions = " OR ".join([f"{style} = true" for style in request.styles])

    sql = text(f"""
        SELECT name, food_type, area, rating, review_count, image_url
        FROM meals
        WHERE food_type = ANY(:food_types)
          AND area ILIKE :region
          {f'AND ({style_conditions})' if style_conditions else ''}
        ORDER BY rating DESC
        LIMIT 10;
    """)

    result = db.execute(sql, {
        "food_types": request.food_types,
        "region": f"%{request.region}%"
    })
    rows = result.fetchall()

    return [
        {
            "name": row[0],
            "food_type": row[1],
            "area": row[2],
            "rating": float(row[3]),
            "review_count": row[4],
            "image_url": row[5]
        }
        for row in rows
    ]

@router.post("/recommend/restaurant")
def recommend_route(request: RecommendRequest, db: Session = Depends(get_db)):
    return recommend_restaurants(request, db)
