import os
import redis
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 동기 DB URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # 비동기 DB URL, env에 없으면 아래 __init__에서 자동 생성
    DATABASE_URL_ASYNC: str = os.getenv("DATABASE_URL_ASYNC", None)

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ODSAY_API_KEY: str = os.getenv("ODSAY_API_KEY")

    def __init__(self):
        # DATABASE_URL_ASYNC가 없으면, asyncpg 드라이버 접두사 추가
        if not self.DATABASE_URL_ASYNC and self.DATABASE_URL:
            self.DATABASE_URL_ASYNC = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

settings = Settings()

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True  # 문자열 자동 디코딩
)
