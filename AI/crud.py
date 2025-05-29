from sqlalchemy.orm import Session
import models, schemas
import json
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: Optional[int] = None):
    # schedule_json이 dict일 경우 str 변환
    schedule_json_str = schedule.schedule_json
    if schedule_json_str and not isinstance(schedule_json_str, str):
        schedule_json_str = json.dumps(schedule_json_str, ensure_ascii=False)

    db_schedule = models.Schedule(
        user_id=user_id,  # user_id가 None이어도 저장 가능하게 models.Schedule 테이블 user_id 컬럼 nullable 처리 필요
        start_city=schedule.startCity,
        end_city=schedule.endCity,
        start_date=schedule.startDate,
        end_date=schedule.endDate,
        emotions=json.dumps(schedule.emotions, ensure_ascii=False),
        companions=json.dumps(schedule.companions, ensure_ascii=False),
        schedule_json=schedule_json_str,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedules_by_user(db: Session, user_id: int):
    return db.query(models.Schedule).filter(models.Schedule.user_id == user_id).all()

def get_schedule(db: Session, schedule_id: int, user_id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id, models.Schedule.user_id == user_id).first()

def update_schedule(db: Session, schedule_id: int, user_id: int, updates: dict):
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    # updates dict에서 필드명을 DB 모델 필드명으로 변환하여 업데이트
    if "startCity" in updates:
        db_schedule.start_city = updates["startCity"]
    if "endCity" in updates:
        db_schedule.end_city = updates["endCity"]
    if "startDate" in updates:
        db_schedule.start_date = updates["startDate"]
    if "endDate" in updates:
        db_schedule.end_date = updates["endDate"]
    if "userEmotion" in updates:
        db_schedule.emotions = json.dumps(updates["userEmotion"], ensure_ascii=False)
    if "companions" in updates:
        db_schedule.companions = json.dumps(updates["companions"], ensure_ascii=False)
    if "schedule_json" in updates:
        # schedule_json은 str 형태로 저장
        if isinstance(updates["schedule_json"], dict):
            db_schedule.schedule_json = json.dumps(updates["schedule_json"], ensure_ascii=False)
        else:
            db_schedule.schedule_json = updates["schedule_json"]

    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int, user_id: int):
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return False
    db.delete(db_schedule)
    db.commit()
    return True

def convert_db_schedule_to_response(db_schedule: models.Schedule) -> schemas.ScheduleDBResponse:
    return schemas.ScheduleDBResponse(
        id=db_schedule.id,
        startCity=db_schedule.start_city,
        endCity=db_schedule.end_city,
        startDate=db_schedule.start_date,
        endDate=db_schedule.end_date,
        userEmotion=json.loads(db_schedule.emotions) if db_schedule.emotions else [],
        with_=json.loads(db_schedule.companions) if db_schedule.companions else [],
        schedule_json=json.loads(db_schedule.schedule_json) if db_schedule.schedule_json else None,
    )

def create_budget(db: Session, schedule_id: int, food_cost: int, entry_fees: int, transport_cost: int):
    total = food_cost + entry_fees + transport_cost
    budget = models.Budget(
        schedule_id=schedule_id,
        food_cost=food_cost,
        entry_fees=entry_fees,
        transport_cost=transport_cost,
        total_budget=total
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

def get_budget_by_schedule_id(db: Session, schedule_id: int):
    return db.query(models.Budget).filter(models.Budget.schedule_id == schedule_id).first()
