import json
from fastapi import APIRouter
from config import redis_client

router = APIRouter()

@router.get("/popular-destinations")
def get_popular_destinations():
    data = redis_client.get("popular_destinations")
    if data:
        # Redis에서 bytes 형태로 꺼내지면 decode 필요
        json_str = data.decode('utf-8') if isinstance(data, bytes) else data
        return json.loads(json_str)
    return []
