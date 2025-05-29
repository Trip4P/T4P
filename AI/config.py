import os
import redis
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True # 문자열 자동 디코딩
)