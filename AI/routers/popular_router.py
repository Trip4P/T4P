# routers/popular_router.py

from fastapi import APIRouter
import json
from config import redis_client

router = APIRouter()

@router.get("/popular-places")
def get_popular_places():
    data = redis_client.get("popular_places")
    if data:
        return json.loads(data)
    return []
