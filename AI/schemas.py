from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# 사용자 생성 요청
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 사용자 응답
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

# 스케줄 요청용 기본 스키마
class ScheduleBase(BaseModel):
    endCity: str
    startDate: str
    endDate: str
    userEmotion: List[str]
    with_: List[str] = Field(..., alias="companions")

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

# 스케줄 생성 요청
class ScheduleCreate(BaseModel):
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

# 장소 정보 (GPT 응답 구조에 맞춤)
class PlaceInfo(BaseModel):
    time: Optional[str]
    name: str = Field(..., alias="place")
    place_id: Optional[str] = Field(None, alias="placeId")
    aiComment: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

# 하루 단위 일정
class ScheduleDayPlan(BaseModel):
    day: int
    schedule: List[PlaceInfo]

# GPT 응답용 스케줄 응답
class ScheduleResponse(BaseModel):
    aiEmpathy: Optional[str] = ""
    tags: Optional[List[str]] = []
    plans: List[ScheduleDayPlan]

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

# DB에서 스케줄 조회 응답
class ScheduleDBResponse(BaseModel):
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

# 스케줄 수정 요청
class ScheduleUpdate(BaseModel):
    endCity: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    userEmotion: Optional[List[str]]
    with_: Optional[List[str]] = Field(None, alias="companions")
    schedule_json: Optional[Dict[str, Any]]

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

class RestaurantPlace(BaseModel):
    name: str
    aiFoodComment: str
    tags: List[str]
    placeId: int
    imageUrl: str  # 이미지 URL 추가

# 로그인 토큰 응답
class Token(BaseModel):
    access_token: str
    token_type: str

# 예산 응답
class DBBudgetResponse(BaseModel):
    id: int
    schedule_id: int
    food_cost: int
    entry_fees: int
    transport_cost: int
    total_budget: int
    created_at: str 

    class Config:
        orm_mode = True

# 예산 요청 (예: 일정에 포함된 장소 목록)
class ScheduleItem(BaseModel):
    place_id: str
    time: Optional[str] = None
    placeType: Optional[str] = None
    place: Optional[str] = None

# 예산 요청 본문
class PlanBudgetRequest(BaseModel):
    plans: Dict[str, List[ScheduleItem]]

# 예산 응답 카테고리
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
    categoryBreakdown: List[Dict[str, int]] 
    aiComment: str

