from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db
import crud, services, schemas
import json

router = APIRouter(prefix="/budget", tags=["budget"])

@router.post("/{schedule_id}", response_model=schemas.BudgetResponse)
def generate_budget(schedule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db, schedule_id, current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    try:
        plan_json = json.loads(schedule.schedule_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid schedule JSON")

    num_people = 1 # 임시로 1명으로 설정

    food_cost = services.calculate_food_cost(db, plan_json, num_people=num_people)
    entry_fees = services.estimate_entry_fees(db, plan_json)
    transport_cost = services.calculate_transport_cost(db, plan_json)

    budget = crud.create_budget(db, schedule_id, food_cost, entry_fees, transport_cost)
    return budget
