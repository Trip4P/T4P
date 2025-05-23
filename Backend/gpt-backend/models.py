from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)

    schedules = relationship("Schedule", back_populates="owner")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_city = Column(String)
    end_city = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    emotions = Column(String)
    companions = Column(String)
    schedule_json = Column(Text)

    owner = relationship("User", back_populates="schedules")
