from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import schemas, crud
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.get("/", response_model=List[schemas.ScheduleDBResponse])
def read_schedules(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_schedules = crud.get_schedules_by_user(db, current_user.id)
    return [crud.convert_db_schedule_to_response(s) for s in db_schedules]

@router.get("/{schedule_id}", response_model=schemas.ScheduleDBResponse)
def read_schedule(schedule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_schedule = crud.get_schedule(db, schedule_id, current_user.id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return crud.convert_db_schedule_to_response(db_schedule)

@router.post("/", response_model=schemas.ScheduleDBResponse)
def create_schedule(schedule: schemas.ScheduleCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_schedule = crud.create_schedule(db, schedule, current_user.id)
    return crud.convert_db_schedule_to_response(db_schedule)

@router.put("/{schedule_id}", response_model=schemas.ScheduleDBResponse)
def update_schedule(schedule_id: int, schedule_update: schemas.ScheduleUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    updated_schedule = crud.update_schedule(db, schedule_id, current_user.id, schedule_update.dict(by_alias=True, exclude_unset=True))
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return crud.convert_db_schedule_to_response(updated_schedule)

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = crud.delete_schedule(db, schedule_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
