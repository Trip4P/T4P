from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import BudgetRequest, BudgetResponse
from services import budget_service

router = APIRouter(prefix="/api/schedules", tags=["budgets"])

@router.post("/budgets", response_model=BudgetResponse)
async def calculate_budget_from_schedule_data(
    request: BudgetRequest,
    db: Session = Depends(get_db)
):
    raw_result = await budget_service.calculate_total_budget_from_plan(db, request)

    category_dict = {
        "교통": raw_result["transport_cost"],
        "숙소": raw_result["accommodation_cost"],
        "식비": raw_result["food_cost"],
    }
    
    if raw_result["entry_fees"] > 0:
        category_dict["관광"] = raw_result["entry_fees"]

    category_breakdown_list = [{k: v} for k, v in category_dict.items() if v > 0]

    return BudgetResponse(
        totalBudget=raw_result["total_cost"],
        categoryBreakdown=category_breakdown_list,
        aiComment=raw_result["comment"]
    )