from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

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
    with_: List[str] = Field(..., alias="companions")  # companions 필드와 매핑

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class ScheduleCreate(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    emotions: List[str]
    companions: Optional[List[str]] = []
    schedule_json: str

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class PlaceInfo(BaseModel):
    name: str
    place_id: str
    description: Optional[str] = None

class ScheduleResponse(BaseModel):
    schedule: Dict[str, List[PlaceInfo]]

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class ScheduleDBResponse(BaseModel):
    id: int
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    userEmotion: List[str]
    with_: List[str] = Field(..., alias="companions")
    schedule_json: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class ScheduleUpdate(BaseModel):
    startCity: Optional[str]
    endCity: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    userEmotion: Optional[List[str]]
    with_: Optional[List[str]] = Field(None, alias="companions")
    schedule_json: Optional[str]

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class Token(BaseModel):
    access_token: str
    token_type: str
