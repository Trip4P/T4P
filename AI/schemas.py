from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    userEmotion: List[str]
    with_: List[str]

class ScheduleCreate(ScheduleBase):
    schedule_json: Optional[dict] = None  # 기본값 None 추가

class PlaceInfo(BaseModel):
    name: str
    place_id: str
    description: Optional[str] = None

class ScheduleResponse(BaseModel):
    schedule: Dict[str, List[PlaceInfo]]

    class Config:
        orm_mode = True

class ScheduleUpdate(BaseModel):
    startCity: Optional[str]
    endCity: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    userEmotion: Optional[List[str]]
    with_: Optional[List[str]]
    schedule_json: Optional[dict] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
