from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableMap
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv(dotenv_path='../../.env')

# 파일 경로
place_path = 'dummy_data/destinations.csv'
meal_path = 'dummy_data/meals.csv'

# 데이터 로딩
df_dest = pd.read_csv(place_path)
df_meal = pd.read_csv(meal_path)

# 감정 매핑
emotion_style_map = {
    "기쁨": ["style_hotplace", "style_activity", "style_photo", "style_shopping"],
    "슬픔": ["style_healing", "style_nature", "style_culture"],
    "화남": ["style_nature", "style_exotic", "style_culture"],
    "지침": ["style_healing", "style_landmark", "style_nature"],
    "불안": ["style_culture", "style_photo", "style_healing"]
}

# 사용자 입력
depart = '부산'
emotion = '기쁨'  # 매핑 가능한 감정으로 변경
days = '2025.05.18 - 2025.05.21'
companion_type = '친구와'

relvant_styles = emotion_style_map.get(emotion, [])
filtered_dest = df_dest[df_dest[relvant_styles].any(axis=1)].sample(n=5, random_state=42)
place_list = filtered_dest['name'].tolist()
res_list = df_meal.sample(n=5, random_state=42)['name'].tolist()

# 모델 준비
llm = ChatOpenAI(temperature=0.8, max_tokens=1500)

# 프롬프트 템플릿
template1 = ChatPromptTemplate.from_messages([
    ("system", "당신은 감성 여행 플래너입니다."),
    ("user", """사용자의 감정은 {emotion}이고, 아래의 {places}과 {res} 리스트에서 알맞는 장소와 식당을 하나씩 추천하고,
일정을 구성해주세요. 출발지는 {depart}, 여행 기간은 {days}, {companion_type} 함께 여행합니다.""")
])

template2 = ChatPromptTemplate.from_messages([
    ("system", "당신은 여행 예산 전문가입니다."),
    ("user", """사용자의 여행 일정은 {result}입니다. 이 일정에 맞춰 예산을 작성하고, 예산에 대한 한 줄 평도 작성해주세요.""")
])

# Runnable 설정
# 1. 사용자 입력 전달
input_mapper = RunnableLambda(lambda _: {
    "emotion": emotion,
    "places": "\n".join([f"- {place}" for place in place_list]),
    "res": "\n".join([f"- {res}" for res in res_list]),
    "depart": depart,
    "days": days,
    "companion_type": companion_type
})

# 2. 여행 일정 생성
trip_chain = input_mapper | template1 | llm

# 3. 예산 추천 체인
budget_chain = RunnableLambda(lambda result: {"result": result}) | template2 | llm

# 4. 전체 체인 연결
full_chain = trip_chain | budget_chain

# 실행
plan_result = trip_chain.invoke({})
final_result = full_chain.invoke({})
print(plan_result.content,'\n')
print(final_result.content)