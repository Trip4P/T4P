import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud, models
from database import get_db
from auth import get_current_user_optional  # 인증 선택적 함수
from services.gpt_service import get_ai_schedule

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/schedule", response_model=schemas.ScheduleResponse)
def recommend_schedule(
    schedule: schemas.ScheduleCreate,
    current_user=Depends(get_current_user_optional),  # 로그인 선택적 처리
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None

    try:
        ai_response = get_ai_schedule(
            db=db,
            start_city=schedule.startCity,
            end_city=schedule.endCity,
            start_date=schedule.startDate,
            end_date=schedule.endDate,
            emotions=schedule.emotions,
            companions=schedule.companions or [],
            food_types=schedule.food_types,
            region=schedule.region
        )

        if not isinstance(ai_response, str):
            ai_response_str = json.dumps(ai_response, ensure_ascii=False)
        else:
            ai_response_str = ai_response

        schedule.schedule_json = ai_response_str

        new_schedule = crud.create_schedule(db, schedule, user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 실패 또는 저장 실패: {str(e)}")

    schedule_dict_raw = json.loads(new_schedule.schedule_json)

    schedule_dict = {}
    for day, places in schedule_dict_raw.items():
        place_objs = []
        for place in places:
            if isinstance(place, dict):
                place_info_data = {
                    "name": place.get("name", "이름 없음"),
                    "place_id": place.get("place_id") or "",  # None일 경우 빈 문자열 처리
                    "description": place.get("description") or "설명 없음"
                }
                place_objs.append(schemas.PlaceInfo(**place_info_data))
            else:
                place_objs.append(schemas.PlaceInfo(name=str(place), place_id="", description="설명 없음"))
        schedule_dict[day] = place_objs

    return schemas.ScheduleResponse(schedule=schedule_dict)