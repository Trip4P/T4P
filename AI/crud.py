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
    schedule_json = schedule.schedule_json

    # schedule_json이 None이거나 plans가 없으면 기본값 넣기
    if not schedule_json:
        schedule_json = {
            "plans": {
                "day1": {
                    "schedule": []
                }
            }
        }
    else:
        # dict인 경우 plans 키 유무 체크
        if isinstance(schedule_json, dict):
            if "plans" not in schedule_json or not schedule_json["plans"]:
                schedule_json["plans"] = {
                    "day1": {
                        "schedule": []
                    }
                }
        elif isinstance(schedule_json, str):
            try:
                parsed = json.loads(schedule_json)
                if "plans" not in parsed or not parsed["plans"]:
                    parsed["plans"] = {
                        "day1": {
                            "schedule": []
                        }
                    }
                schedule_json = parsed
            except Exception:
                schedule_json = {
                    "plans": {
                        "day1": {
                            "schedule": []
                        }
                    }
                }

    schedule_json_str = json.dumps(schedule_json, ensure_ascii=False)

    db_schedule = models.Schedule(
        user_id=user_id,
        start_city=schedule.startCity,
        end_city=schedule.endCity,
        start_date=schedule.startDate,
        end_date=schedule.endDate,
        emotions=json.dumps(schedule.emotions, ensure_ascii=False) if schedule.emotions else None,
        companions=json.dumps(schedule.companions, ensure_ascii=False) if schedule.companions else None,
        schedule_json=schedule_json_str,
        people_count=schedule.peopleCount
        # tags, aiEmpathy, plans 는 DB 저장 대상 아님
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

    # 기본 필드 업데이트
    if "startCity" in updates:
        db_schedule.start_city = updates["startCity"]
    if "endCity" in updates:
        db_schedule.end_city = updates["endCity"]
    if "startDate" in updates:
        db_schedule.start_date = updates["startDate"]
    if "endDate" in updates:
        db_schedule.end_date = updates["endDate"]

    if "userEmotion" in updates:
        db_schedule.emotions = json.dumps(updates["userEmotion"], ensure_ascii=False) if updates["userEmotion"] else None

    if "companions" in updates:
        db_schedule.companions = json.dumps(updates["companions"], ensure_ascii=False) if updates["companions"] else None

    # schedule_json 업데이트 처리 (dict이면 JSON 문자열로 변환)
    if "schedule_json" in updates:
        # schedule_json 내부가 dict일 수도 있고, string일 수도 있으니 검사
        if isinstance(updates["schedule_json"], dict):
            # 기존 schedule_json이 문자열인 경우 덮어쓰기
            db_schedule.schedule_json = json.dumps(updates["schedule_json"], ensure_ascii=False)
        else:
            db_schedule.schedule_json = updates["schedule_json"]

    # AI empathy, tags, plans 등은 DB 저장 대상 아님(필요하면 따로 컬럼 추가 필요)

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
        startCity=db_schedule.start_city,
        endCity=db_schedule.end_city,
        startDate=db_schedule.start_date,
        endDate=db_schedule.end_date,
        userEmotion=json.loads(db_schedule.emotions) if db_schedule.emotions else [],
        with_=json.loads(db_schedule.companions) if db_schedule.companions else [],
        schedule_json=json.loads(db_schedule.schedule_json) if db_schedule.schedule_json else None,
        aiEmpathy=None,  # DB에서 안 가져옴
        tags=[],         # DB에서 안 가져옴
        plans=[]         # DB에서 안 가져옴
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
