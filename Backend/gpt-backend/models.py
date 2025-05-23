from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON, ForeignKey

from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

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
    # latitude = Column(Float)
    # longitude = Column(Float)

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
    style_date = Column(Boolean)
    style_business = Column(Boolean)
    style_anniversary = Column(Boolean)
    style_team = Column(Boolean)
    style_family = Column(Boolean)
    style_view = Column(Boolean)
    style_meeting = Column(Boolean)
    style_quiet = Column(Boolean)
    style_modern = Column(Boolean)
    style_traditional = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    place_id = Column(String, unique=True, index=True)
    area = Column(Text)
    opening_periods = Column(JSON)
    # latitude = Column(Float)
    # longitude = Column(Float) 추후추가...

class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    food_cost = Column(Integer)
    transport_cost = Column(Integer)
    entry_fees = Column(Integer)
    total_budget = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
