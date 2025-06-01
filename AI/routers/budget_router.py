from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import services, schemas, crud
from models import Budget
from schemas import BudgetRequest, BudgetResponse, CategoryItem
from services import budget_service
router = APIRouter(prefix="/api/schedules", tags=["budgets"])

@router.post("/budgets", response_model=BudgetResponse)
def calculate_budget_from_schedule_data(request: BudgetRequest, db: Session = Depends(get_db)):
    raw_result = budget_service.calculate_total_budget_from_plan(db, request)

    category_dict = {
        "교통": raw_result["transport_cost"],
        "식비": raw_result["food_cost"],
        "관광": raw_result["entry_fees"]
    }

    # key, value 쌍을 각각 하나의 딕셔너리로 만들어 리스트로 변환
    category_breakdown_list = [{k: v} for k, v in category_dict.items()]

    return BudgetResponse(
        totalBudget=raw_result["total_cost"],
        categoryBreakdown=category_breakdown_list,
        aiComment=raw_result["comment"]
    )

