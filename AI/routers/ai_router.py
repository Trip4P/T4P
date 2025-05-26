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
            emotions=schedule.emotions,
            companions=schedule.companions or [],
        )

        # ai_response가 dict라면 str로 변환
        if not isinstance(ai_response, str):
            ai_response_str = json.dumps(ai_response, ensure_ascii=False)
        else:
            ai_response_str = ai_response

        # schedule_json 필드에 AI 응답 문자열 저장
        schedule.schedule_json = ai_response_str

        new_schedule = crud.create_schedule(db, schedule, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 실패 또는 저장 실패: {str(e)}")

    schedule_dict_raw = json.loads(new_schedule.schedule_json)

    schedule_dict = {
        day: [schemas.PlaceInfo(**place) for place in places]
        for day, places in schedule_dict_raw.items()
    }

    return schemas.ScheduleResponse(schedule=schedule_dict)
