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
    peopleCount: Optional[int] = 1
    aiEmpathy: Optional[str] = None
    tags: Optional[List[str]] = []
    plans: Optional[Dict[str, Any]] = {}
    schedule_json: Optional[Dict[str, Any]] = {}

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class PlaceInfo(BaseModel):
    time: Optional[str]
    name: str = Field(..., alias="place")  # GPT에서 place로 옴
    place_id: Optional[int] = Field(None, alias="placeId")
    aiComment: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class DayPlan(BaseModel):
    schedule: List[PlaceInfo]

class ScheduleResponse(BaseModel):
    aiEmpathy: Optional[str] = ""
    tags: Optional[List[str]] = []
    plans: Dict[str, DayPlan] = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class ScheduleDBResponse(BaseModel):
    startCity: str
    endCity: str
    startDate: str
    endDate: str
    userEmotion: List[str]
    with_: List[str] = Field(..., alias="companions")
    food_types: List[str]
    region: Optional[str] = None
    aiEmpathy: Optional[str] = None
    tags: Optional[List[str]] = []
    plans: Optional[Dict[str, Any]] = {}
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
    schedule_json: Optional[Dict[str, Any]]

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BudgetResponse(BaseModel):
    id: int
    schedule_id: int
    food_cost: int
    entry_fees: int
    transport_cost: int
    total_budget: int
    created_at: str 

    class Config:
        orm_mode = True  # Pydantic 모델로 변환

# 예산요청 스키마
class ScheduleItem(BaseModel):
    place_id: str  
    time: Optional[str] = None
    placeType: Optional[str] = None
    place: Optional[str] = None  

class PlanBudgetRequest(BaseModel):
    plans: Dict[str, List[ScheduleItem]]

class CategoryBreakdown(BaseModel):
    교통: int
    식비: int
    관광: int

class PlanBudgetResponse(BaseModel):
    totalBudget: int
    categoryBreakdown: CategoryBreakdown