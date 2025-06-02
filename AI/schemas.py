from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel

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
    food_types: List[str]
    region: str
    schedule_json: Optional[Dict[str, Any]] = {}

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class PlaceInfo(BaseModel):
    name: str
    place_id: Optional[str] = None
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

#예산요청 스키마
class ScheduleItem(BaseModel):
    place_id: str  
    time: Optional[str] = None
    placeType: Optional[str] = None
    place: Optional[str] = None  

class PlanBudgetRequest(BaseModel):
    plans: Dict[str, List[ScheduleItem]]

class CategoryBreakdown(BaseModel):
    식비: int
    교통: int
    관광: int

class PlanBudgetResponse(BaseModel):
    totalBudget: int
    categoryBreakdown: CategoryBreakdown
    aiComment: str

#예산요청 스키마2
class SchedulePlace(BaseModel):
    time: str
    place: str
    placeId: int
    pricelevel: int
    latitude: float
    longitude: float

class PlanItem(BaseModel):
    day: int
    schedule: List[SchedulePlace]

class BudgetRequest(BaseModel):
    plans: List[PlanItem]
    peopleCount: int

class CategoryItem(BaseModel):
    category: str
    amount: int

class BudgetResponse(BaseModel):
    totalBudget: int
    categoryBreakdown: List[Dict[str, int]]  # key가 카테고리명, value가 금액인 dict 리스트
    aiComment: str
