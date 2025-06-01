import json
from database import get_db
from config import redis_client
from sqlalchemy import text

def update_popular_destinations():
    print("DB 연결 시작")
    db = next(get_db())
    print("DB 연결 성공")

    result = db.execute(text("""
        SELECT end_city AS destination, COUNT(*) AS count
        FROM schedules
        GROUP BY end_city
        ORDER BY count DESC
        LIMIT 9
    """))
    print("쿼리 실행 완료")

    destinations = [{"destination": row[0], "count": row[1]} for row in result.fetchall()]
    print("결과 파싱 완료:", destinations)

    redis_client.set("popular_destinations", json.dumps(destinations))  # json 문자열로 저장
    print("인기 여행지 Redis 캐싱 완료")
