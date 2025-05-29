from datetime import datetime, date
from typing import List
import json
import logging

from sqlalchemy.orm import Session
from openai import OpenAI

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import QuickBudget
from config import settings 


# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_gpt_budget_comment(total_cost: int, end_city: str, days: int, num_people: int) -> str:
    prompt = f"""
{end_city}에서 {days}일간 {num_people}명이 여행할 때 예상 총 비용은 약 {total_cost:,}원입니다.
숙소비를 제외한 식비, 입장료 및 체험비, 그리고 지역 내 대중교통비만 포함한 비용입니다.
최고의 여행 예산 평가 도우미인 당신이 예산에 대해 두세 문장으로 간단히 평가해 주세요. 
평가를 할때에는 몇명과 함께하는 몇일짜리 여행인지도 언급해주세요. 비교군이 없으니 가성비, 넉넉하다, 빠듯하다같은 느낌은 피해주세요.
👉 "~같아요", "~일 것 같아요", "~하면 좋겠어요"처럼 부드러운 말투로.
👉 MZ세대 감성 이모지를 센스 있게 활용해줘.
👉 설명하지 말고, 친구에게 말하듯 자연스럽고 공감되는 한두 문장으로만 말해줘.
예: "살짝 비싸지만 그만한 가치가 있을 것 같아요 ✨", "가성비 최고 코스예요! 😎👍"
👉 비용 느낌뿐 아니라, '왜 그렇게 느껴질 수 있는지'를 센스 있게 살짝 덧붙여줘.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "여행 예산 평가 도우미"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("GPT 코멘트 생성 실패")
        return "예산에 대한 평가를 불러오는 데 실패했습니다."


def quick_budget(
    start_city: str,
    end_city: str,
    start_date: date,
    end_date: date,
    num_people: int,
    db: Session
) -> dict:
    days = (end_date - start_date).days + 1  # 여행 기간 계산 (포함)

    prompt = f"""
'{start_city}'에서 '{end_city}'까지 {days}일간 {num_people}명이 여행할 경우 예상 평균 여행비용을 알려줘.
- 항목: 식비, 체험비/입장료, 교통비
- 각 항목별 1인당 1일 기준 평균비용을 한국 원화로 알려줘.
- 단위는 원으로, 숫자만, 소수점 없이 응답해줘.
- 아래처럼 JSON으로 응답해줘:

{{"food": 10000, "entry": 12000, "transport": 7000}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 똑똑한 여행 비용 추정 도우미야. 정확하고 간결하게 응답해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )

        raw_content = response.choices[0].message.content.strip()

        # 코드블록 제거 처리
        if raw_content.startswith("```json"):
            raw_content = raw_content[len("```json"):].strip()
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3].strip()

        cost_json = json.loads(raw_content)

        food_cost = cost_json["food"] * num_people * days
        entry_fees = cost_json["entry"] * num_people * days
        transport_cost = cost_json["transport"] * num_people * days
        total_cost = food_cost + entry_fees + transport_cost

        comment = ask_gpt_budget_comment(total_cost, end_city, days=days, num_people=num_people)

        new_budget = QuickBudget(
            start_city=start_city,
            end_city=end_city,
            start_date=start_date,
            end_date=end_date,
            num_people=num_people,
            food_cost=food_cost,
            entry_fees=entry_fees,
            transport_cost=transport_cost,
            total_budget=total_cost,
            comment=comment,
            created_at=datetime.utcnow()
        )
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)

        return {
            "food_cost": food_cost,
            "entry_fees": entry_fees,
            "transport_cost": transport_cost,
            "total_cost": total_cost,
            "comment": comment
        }

    except json.JSONDecodeError:
        logger.error("GPT 응답 JSON 파싱 실패: %s", response.choices[0].message.content)
        raise
    except Exception:
        logger.exception("GPT quick budget 실패")
        raise
