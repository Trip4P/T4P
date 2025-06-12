import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud, models
from database import get_db
from auth import get_current_user_optional  # 로그인 선택적 처리
from services.gpt_service import get_ai_schedule
import re

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/schedule", response_model=schemas.ScheduleResponse)
def recommend_schedule(
    schedule: schemas.ScheduleCreate,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None

    try:
        # 1) DB에 기본 일정 데이터 저장 (AI 코멘트 제외)
        new_schedule = crud.create_schedule(db, schedule, user_id)

        # 2) 저장된 기본 일정 schedule_json 파싱
        base_schedule_json = new_schedule.schedule_json
        if isinstance(base_schedule_json, str):
            base_schedule_data = json.loads(base_schedule_json)
        elif isinstance(base_schedule_json, dict):
            base_schedule_data = base_schedule_json
        else:
            raise HTTPException(status_code=500, detail="schedule_json 필드가 올바른 형식이 아님")

        base_plans_raw = base_schedule_data.get("plans", None) or {}

        # base_plans를 dict이면 list로 변환
        if isinstance(base_plans_raw, dict):
            base_plans_list = []
            for day_key, base_day in base_plans_raw.items():
                try:
                    day_num = int(''.join(filter(str.isdigit, day_key)))
                except Exception:
                    day_num = 1
                base_plans_list.append({
                    "day": day_num,
                    "schedule": base_day.get("schedule", []) if isinstance(base_day, dict) else []
                })
            base_plans_list.sort(key=lambda x: x["day"])
        elif isinstance(base_plans_raw, list):
            base_plans_list = base_plans_raw
        else:
            base_plans_list = []

        if not base_plans_list or all(len(day.get("schedule", [])) == 0 for day in base_plans_list):
            base_plans_list = [{"day": 1, "schedule": []}]

        # 3) AI 호출
        ai_response = get_ai_schedule(
            db=db,
            end_city=schedule.endCity,
            start_date=schedule.startDate,
            end_date=schedule.endDate,
            emotions=schedule.emotions,
            companions=schedule.companions or [],
            peopleCount=schedule.peopleCount
        )

        if isinstance(ai_response, str):
            ai_response_data = json.loads(ai_response)
        elif hasattr(ai_response, "dict"):
            ai_response_data = ai_response.dict()
        else:
            ai_response_data = ai_response

        ai_plans_raw = ai_response_data.get("plans", {}) or {}

        if isinstance(ai_plans_raw, list):
            ai_plans_list = ai_plans_raw
        elif isinstance(ai_plans_raw, dict):
            ai_plans_list = []
            for day_key, ai_day in ai_plans_raw.items():
                try:
                    day_num = int(''.join(filter(str.isdigit, day_key)))
                except Exception:
                    day_num = 1
                ai_plans_list.append({
                    "day": day_num,
                    "schedule": ai_day.get("schedule", []) if isinstance(ai_day, dict) else []
                })
            ai_plans_list.sort(key=lambda x: x["day"])
        else:
            ai_plans_list = []

        if not ai_plans_list or all(len(day.get("schedule", [])) == 0 for day in ai_plans_list):
            ai_plans_list = [{"day": 1, "schedule": []}]

        # 4) aiComment 붙이기 (base_plans_list 안에 aiComment 추가)
        for base_day in base_plans_list:
            day_num = base_day["day"]
            ai_day = next((d for d in ai_plans_list if d["day"] == day_num), None)
            if ai_day:
                for idx, base_place in enumerate(base_day["schedule"]):
                    if idx < len(ai_day["schedule"]):
                        ai_comment = ai_day["schedule"][idx].get("aiComment", "")
                        base_place["aiComment"] = ai_comment

        # 5) AI plans를 DB에 저장할 형식으로 변환 (dict로 day1, day2 ...)
        plans_to_save = {}
        for day in ai_plans_list:
            day_key = f"day{day['day']}"
            plans_to_save[day_key] = day

        # 6) GPT 응답에서 받은 aiEmpathy와 tags도 저장하도록 추가
        update_data = {
            "schedule_json": {
                "plans": plans_to_save
            },
            "aiEmpathy": ai_response_data.get("aiEmpathy", ""),
            "tags": ai_response_data.get("tags", [])
        }

        updated_schedule = crud.update_schedule(db, new_schedule.id, user_id, update_data)

        # 7) 최종 응답을 위한 dict → list 변환
        plans_list_for_response = []
        for day_key in sorted(plans_to_save.keys(), key=lambda x: int(''.join(filter(str.isdigit, x)))):
            day_data = plans_to_save[day_key]
            plans_list_for_response.append(day_data)

        # 8) 최종 응답 생성
        final_response = schemas.ScheduleResponse(
            aiEmpathy=ai_response_data.get("aiEmpathy", ""),
            tags=ai_response_data.get("tags", []),
            plans=plans_list_for_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 또는 저장 실패: {str(e)}")

    return final_response
