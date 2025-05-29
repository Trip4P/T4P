from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.quick_budget_service import quick_budget
import schemas
import traceback
from datetime import datetime


import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=schemas.PlanBudgetResponse)
def quick_budget_api(
    startCity: str = Body(...),
    endCity: str = Body(...),
    startDate: str = Body(...),
    endDate: str = Body(...),
    peopleNum: int = Body(...),
    db: Session = Depends(get_db)
):
    try:
        # 문자열 → 날짜 변환
        start_date_dt = datetime.strptime(startDate, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(endDate, "%Y-%m-%d").date()

        result = quick_budget(startCity, endCity, start_date_dt, end_date_dt, peopleNum, db)

        return {
            "totalBudget": result["total_cost"],
            "categoryBreakdown": {
                "교통": result["transport_cost"],
                "식비": result["food_cost"],
                "관광": result["entry_fees"],
            },
            "aiComment": result["comment"]
        }
    except Exception as e:
        logger.error(f"빠른 예산 추정 중 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"빠른 예산 추정 중 오류가 발생했습니다: {str(e)}")
