from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import services, schemas, crud
from models import Budget
from services.budget_service import calculate_total_budget_from_schedule_id

router = APIRouter(prefix="/api/schedules", tags=["budgets"])

@router.get("/budgets/{schedule_id}", response_model=schemas.PlanBudgetResponse)
def calculate_budget_by_schedule_id(schedule_id: int, db: Session = Depends(get_db)):
    try:
        print("📌 schedule_id:", schedule_id)

        budget_result = services.calculate_total_budget_from_schedule_id(db, schedule_id)
        print("✅ budget_result:", budget_result)

        saved_budget = services.save_budget(db, schedule_id, budget_result)
        print("✅ saved_budget:", saved_budget)

        response = {
            "totalBudget": budget_result["total_cost"],
            "categoryBreakdown": {
                "교통": budget_result["transport_cost"],
                "식비": budget_result["food_cost"],
                "관광": budget_result["entry_fees"],
            },
            "aiComment": budget_result["comment"]
        }
        print("✅ response:", response)

        return response

    except ValueError as e:
        print("⚠️ ValueError:", str(e))
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        print("❌ 서버 내부 오류:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
