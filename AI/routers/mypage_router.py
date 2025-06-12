from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/mypage", tags=["mypage"])

@router.get("/", response_model=schemas.MyPageResponse)
def get_mypage_info(
    current_user: models.User = Depends(get_current_user)
):
    return {
        "username": current_user.username,
        "email": current_user.email,
    }

@router.get("/schedules", response_model=list[schemas.MySimplePlan])
def get_my_schedules(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    schedules = db.query(models.Schedule).filter_by(user_id=current_user.id).all()
    return schedules
