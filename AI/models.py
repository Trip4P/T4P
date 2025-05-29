from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # 필요시 추가

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    schedules = relationship("Schedule", back_populates="owner")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_city = Column(String)
    end_city = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    emotions = Column(String)       # JSON 문자열 저장
    companions = Column(String)     # JSON 문자열 저장
    schedule_json = Column(Text)

    owner = relationship("User", back_populates="schedules")
