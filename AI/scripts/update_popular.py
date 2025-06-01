import sys
import os
import json

# 루트 경로 추가 (프로젝트 최상위)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.popular_service import update_popular_destinations
from config import redis_client

if __name__ == "__main__":
    update_popular_destinations()

    cached_data = redis_client.get("popular_destinations")
    if cached_data:
        if isinstance(cached_data, bytes):
            cached_data = cached_data.decode("utf-8")
        data = json.loads(cached_data)  # json 문자열 -> 파이썬 리스트/딕셔너리
        print("캐시된 인기 여행지 데이터:", data)
    else:
        print("캐시된 데이터가 없습니다.")
