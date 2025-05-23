from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ScheduleCreate(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    userEmotion: List[str]
    with_: List[str]
    schedule_json: str

class ScheduleResponse(BaseModel):
    id: int
    user_id: int
    start_city: str
    end_city: str
    start_date: str
    end_date: str
    emotions: str
    companions: str
    schedule_json: str

    class Config:
        from_attributes = True

class ScheduleUpdate(BaseModel):
    start_city: Optional[str]
    end_city: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    emotions: Optional[str]
    companions: Optional[str]
    schedule_json: Optional[str]

from pydantic import BaseModel

class BudgetResponse(BaseModel):
    id: int
    schedule_id: int
    food_cost: int
    entry_fees: int
    transport_cost: int
    total_budget: int
    created_at: str 

    class Config:
        orm_mode = True  #Pydantic 모델로 변환


        