from sqlalchemy.orm import Session
import models, schemas
import json, ast
from passlib.context import CryptContext
from typing import Optional
from schemas import ScheduleDBResponse

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

    if not schedule_json:
        schedule_json = {
            "plans": {
                "day1": {
                    "schedule": []
                }
            }
        }
    else:
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
        end_city=schedule.endCity,
        start_date=schedule.startDate,
        end_date=schedule.endDate,
        emotions=json.dumps(schedule.emotions, ensure_ascii=False) if schedule.emotions else None,
        companions=json.dumps(schedule.companions, ensure_ascii=False) if schedule.companions else None,
        schedule_json=schedule_json_str,
        people_count=schedule.peopleCount,
        ai_empathy=schedule.aiEmpathy
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

    if "aiEmpathy" in updates:
        db_schedule.ai_empathy = updates["aiEmpathy"]

    if "tags" in updates:
        db_schedule.tags = json.dumps(updates["tags"], ensure_ascii=False)

    if "schedule_json" in updates:
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

# 안전한 문자열 리스트 파싱 함수
def parse_list_field(value):
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except Exception:
            return []
    return value or []

# 응답 변환 함수
def convert_db_schedule_to_response(db_schedule):
    schedule_json = db_schedule.schedule_json
    if isinstance(schedule_json, str):
        try:
            schedule_json = json.loads(schedule_json)
        except json.JSONDecodeError:
            schedule_json = {}

    return ScheduleDBResponse(
        endCity=db_schedule.end_city,
        startDate=db_schedule.start_date,
        endDate=db_schedule.end_date,
        userEmotion=parse_list_field(db_schedule.emotions),
        companions=parse_list_field(db_schedule.companions),
        aiEmpathy=getattr(db_schedule, "ai_empathy", None),
        tags=parse_list_field(getattr(db_schedule, "tags", [])),
        plans=schedule_json.get("plans", {})
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
