from sqlalchemy.orm import Session
import models, schemas
import json

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str): # 로그인 시, username으로 해당 유저가 존재하는지 확인인
    return db.query(models.User).filter(models.User.username == username).first()

def create_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: int):
    schedule_json_str = schedule.schedule_json
    if isinstance(schedule_json_str, dict):
        schedule_json_str = json.dumps(schedule_json_str, ensure_ascii=False)

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

def get_schedules_by_user(db: Session, user_id: int): # 특정 사용자가 저장한 모든 일정을 조회
    return db.query(models.Schedule).filter(models.Schedule.user_id == user_id).all()

def get_schedule(db: Session, schedule_id: int, user_id: int): # 특정 사용자의 특정 일정 한 개만 조회
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id, models.Schedule.user_id == user_id).first()

def update_schedule(db: Session, schedule_id: int, user_id: int, updated_data: dict):
    schedule = get_schedule(db, schedule_id, user_id)
    if not schedule:
        return None
    for key, value in updated_data.items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule

def delete_schedule(db: Session, schedule_id: int, user_id: int):
    schedule = get_schedule(db, schedule_id, user_id)
    if not schedule:
        return None
    db.delete(schedule)
    db.commit()
    return schedule
