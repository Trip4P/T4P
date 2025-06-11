import json
from sqlalchemy import text
from config import redis_client
from database import get_db

DEFAULT_IMAGE = "https://cdn.example.com/images/default.jpg"

def update_popular_places():
    db = next(get_db())

    result = db.execute(text("""
        SELECT place_id, COUNT(*) as count
        FROM ai_schedule_places
        GROUP BY place_id
        ORDER BY count DESC
        LIMIT 16
    """)).fetchall()

    popular = []
    for row in result:
        place_id = row[0]
        count = row[1]

        # 관광지에서 조회
        place = db.execute(text("""
            SELECT name, COALESCE(image_url, '') as image_url, '관광지' as type
            FROM destinations
            WHERE place_id = :pid
        """), {"pid": place_id}).fetchone()

        # 맛집에서 조회
        if not place:
            place = db.execute(text("""
                SELECT name, COALESCE(image_url, '') as image_url, '맛집' as type
                FROM meals
                WHERE place_id = :pid
            """), {"pid": place_id}).fetchone()

        # 숙소에서 조회
        if not place:
            place = db.execute(text("""
                SELECT name, COALESCE(image_url, '') as image_url, '숙소' as type
                FROM accommodations
                WHERE place_id = :pid
            """), {"pid": place_id}).fetchone()

        if place:
            name, image_url, place_type = place
            popular.append({
                "placeId": place_id,
                "name": name,
                "type": place_type,
                "count": count,
                "imageUrl": image_url if image_url else DEFAULT_IMAGE
            })

    redis_client.set("popular_places", json.dumps(popular, ensure_ascii=False))
    print("인기 장소 Redis 캐싱 완료")
