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
    startCity: str
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

# 스케줄 수정 요청
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

# 예산 응답 카테고리
class CategoryBreakdown(BaseModel):
    식비: int
    교통: int
    관광: int

class PlanBudgetResponse(BaseModel):
    totalBudget: int
    categoryBreakdown: CategoryBreakdown
    aiComment: str

#예산요청 스키마
class SchedulePlace(BaseModel):
    time: str
    place: str
    placeId: str  
    pricelevel: int
    latitude: float
    longitude: float


class PlanItem(BaseModel):
    day: int
    schedule: List[SchedulePlace]

class BudgetRequest(BaseModel):
    plans: List[PlanItem]
    peopleCount: int
    endCity: str

class BudgetResponse(BaseModel):
    totalBudget: int
    categoryBreakdown: List[Dict[str, int]] 
    aiComment: str

