import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db
from auth import get_current_user
from services.gpt_service import get_ai_schedule

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/schedule", response_model=schemas.ScheduleResponse)
def recommend_schedule(
    schedule: schemas.ScheduleCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
            schedule_json=ai_response,
        ),
        current_user.id,
    )

    # schedule_json 문자열을 파싱해서 PlaceInfo 리스트 딕셔너리로 변환
    schedule_dict_raw = json.loads(new_schedule.schedule_json)
    schedule_dict = {
        day: [schemas.PlaceInfo(**place) for place in places]
        for day, places in schedule_dict_raw.items()
    }

    return schemas.ScheduleResponse(schedule=schedule_dict)
