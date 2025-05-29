import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 환경변수 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")

# DB 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (ORM 모델들의 공통 부모)
Base = declarative_base()

# DB 초기화 함수 (테이블 생성)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency: 요청마다 DB 세션 생성/종료
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
