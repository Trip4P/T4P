from sqlalchemy.orm import Session
import models, schemas
import json
from passlib.context import CryptContext

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

def create_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: int):
    schedule_json_str = json.dumps(schedule.schedule_json, ensure_ascii=False) if schedule.schedule_json else ""

    db_schedule = models.Schedule(
        user_id=user_id,
        start_city=schedule.startCity,
        end_city=schedule.endCity,
        start_date=schedule.startDate,
        end_date=schedule.endDate,
        emotions=",".join(schedule.userEmotion),
        companions=",".join(schedule.with_),
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
