# routers/schedule_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import schemas, crud
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.get("/", response_model=List[schemas.ScheduleResponse])
def read_schedules(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_schedules_by_user(db, current_user.id)

@router.get("/{schedule_id}", response_model=schemas.ScheduleResponse)
def read_schedule(schedule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db, schedule_id, current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/", response_model=schemas.ScheduleResponse)
def create_schedule(schedule: schemas.ScheduleCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_schedule(db, schedule, current_user.id)

@router.put("/{schedule_id}", response_model=schemas.ScheduleResponse)
def update_schedule(schedule_id: int, schedule_update: schemas.ScheduleUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    updated = crud.update_schedule(db, schedule_id, current_user.id, schedule_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = crud.delete_schedule(db, schedule_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
