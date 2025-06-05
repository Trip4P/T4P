from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

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
    emotions = Column(String)       
    companions = Column(String)     
    schedule_json = Column(Text)
    people_count = Column(Integer, default=1)

    owner = relationship("User", back_populates="schedules")

class Place(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    city: str
    type: str  # 예: 'meal', 'destination', 'accommodation'

    class Config:
        from_attributes = True
        validate_by_name = True

class Destination(Base):
    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    area = Column(Text)
    location = Column(Text)
    rating = Column(Float)
    review_count = Column(Integer)
    price_level = Column(Integer)
    phone_number = Column(String)
    opening_hours = Column(Text)
    image_url = Column(Text)
    style_activity = Column(Boolean)
    style_hotplace = Column(Boolean)
    style_nature = Column(Boolean)
    style_landmark = Column(Boolean)
    style_healing = Column(Boolean)
    style_culture = Column(Boolean)
    style_photo = Column(Boolean)
    style_shopping = Column(Boolean)
    style_exotic = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    place_id = Column(String, unique=True, index=True)
    opening_periods = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    keywords = Column(JSON)

    reviews = relationship("Review", back_populates="destination")

class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    food_type = Column(String)
    location = Column(Text)
    price_level = Column(Integer)
    rating = Column(Float)
    review_count = Column(Integer)
    phone_number = Column(String)
    opening_hours = Column(Text)
    image_url = Column(Text)
    place_id = Column(String, unique=True, index=True)
    opening_periods = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    keywords = Column(JSON)

    reviews = relationship("Review", back_populates="meal")

class Accommodation(Base):
    __tablename__ = 'accommodations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(Text)
    price = Column(Integer)
    rating = Column(String)
    review_count = Column(Integer)
    phone_number = Column(String)
    opening_hours = Column(Text)
    image_url = Column(Text)
    place_id = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    category = Column(Text, nullable=True)  # 예: 호텔, 게스트하우스 등

    reviews = relationship("Review", back_populates="accommodation")


class Budget(Base):
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    food_cost = Column(Integer)
    transport_cost = Column(Integer)
    entry_fees = Column(Integer)
    total_budget = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(String, nullable=True)

class QuickBudget(Base):
    __tablename__ = 'quick_budget' 

    id = Column(Integer, primary_key=True, index=True)

    # 사용자가 입력한 여행 정보
    start_city = Column(String)
    end_city = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    num_people = Column(Integer)

    # 예산 결과
    food_cost = Column(Integer)
    transport_cost = Column(Integer)
    entry_fees = Column(Integer)
    total_budget = Column(Integer)
    comment = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey('meals.id', ondelete='CASCADE'), nullable=True)  # Integer 유지
    destination_id = Column(Integer, ForeignKey('destinations.id', ondelete='CASCADE'), nullable=True)  # Integer 유지
    accommodation_id = Column(Integer, ForeignKey('accommodations.id', ondelete='CASCADE'), nullable=True)  # Integer 유지
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(String, nullable=False)

    meal = relationship("Meal", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")
    accommodation = relationship("Accommodation", back_populates="reviews")
