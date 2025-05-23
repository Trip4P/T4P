from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, crud, auth
from database import get_db
from typing import List
from services.gpt_service import get_ai_schedule

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.get("/", response_model=List[schemas.ScheduleResponse])
def read_schedules(current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    schedules = crud.get_schedules_by_user(db, current_user.id)
    return schedules

@router.get("/{schedule_id}", response_model=schemas.ScheduleResponse)
def read_schedule(schedule_id: int, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db, schedule_id, current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/", response_model=schemas.ScheduleResponse)
def create_schedule(schedule: schemas.ScheduleCreate, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_schedule = crud.create_schedule(db, schedule, current_user.id)
    return new_schedule

@router.post("/recommend", response_model=schemas.ScheduleResponse)
def recommend_schedule(schedule: schemas.ScheduleCreate, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    try:
        ai_response = get_ai_schedule(
            start_city=schedule.startCity,
            end_city=schedule.endCity,
            start_date=schedule.startDate,
            end_date=schedule.endDate,
            emotions=schedule.userEmotion,
            companions=schedule.with_,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 실패: {str(e)}")
    
    new_schedule = crud.create_schedule(
        db,
        schemas.ScheduleCreate(
            startCity=schedule.startCity,
            endCity=schedule.endCity,
            startDate=schedule.startDate,
            endDate=schedule.endDate,
            userEmotion=schedule.userEmotion,
            with_=schedule.with_,
            schedule_json=ai_response
        ),
        current_user.id
    )
    return new_schedule

@router.put("/{schedule_id}", response_model=schemas.ScheduleResponse)
def update_schedule(schedule_id: int, schedule_update: schemas.ScheduleUpdate, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    updated_schedule = crud.update_schedule(db, schedule_id, current_user.id, schedule_update.dict(exclude_unset=True))
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated_schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    schedule = crud.delete_schedule(db, schedule_id, current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return
