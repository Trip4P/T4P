from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv(dotenv_path= '../../.env')

place_path= 'dummy_data/destinations.csv'
meal_path= 'dummy_data/meals.csv'

df_dest = pd.read_csv(place_path)
df_meal = pd.read_csv(meal_path)

emotion_style_map = {
    "기쁨": ["style_hotplace", "style_activity", "style_photo", "style_shopping"],
    "슬픔": ["style_healing", "style_nature", "style_culture"],
    "화남": ["style_nature", "style_exotic", "style_culture"],
    "지침": ["style_healing", "style_landmark", "style_nature"],
    "불안": ["style_culture", "style_photo", "style_healing"]
}

#사용자 입력값들
depart = '부산'
emotion = '설레는'
days = '2025.05.18 - 2025.05.21'
companion_type = '친구와'

relvant_styles = emotion_style_map.get(emotion,[])

filtered_dest = df_dest[df_dest[relvant_styles].any(axis=1)].sample(n=5, random_state=42)
place_list = filtered_dest['name'].tolist()
res_list = df_meal.sample(n=5, random_state=42)['name'].tolist()

template = ChatPromptTemplate.from_messages([
    ("system", "당신은 감성 여행 플래너입니다. 사용자의 감정을 기반으로 여행일정을 생성해주고자 합니다."),
    ("user", """사용자의 감정은 {emotion}이고, 아래의 {places}과 {res} 리스트에서 사용자의 감정에 알맞는 장소와 식당을 하나씩 추천해주고,
     이를 바탕으로 전체적인 여행 일정을 짜주시오. 사용자는 {depart}에서 출발하고, 여행 기간은 {days}입니다. {companion_type} 함께 여행을 할 예정이야. 날짜를 보고 계절도 고려해서 일정을 짜줘.
     장소를 선정한 이유도 감성적이고 친근하되 너무 장황하지 않게 3-4 문장 정도로 알려줘.
     

    예시)
    장소: 서울숲 
    맛집: 포케올데이
    경복궁을 추천해드릴게요. 조용히 돌담길을 따라 걷다 보면 마음이 조금은 가벼워질 수 있습니다.  
    도심 속 자연이 주는 고요함과 고즈넉한 풍경이 슬픈 감정을 부드럽게 감싸줄 것입니다. 
    눈이 온다면 또다른 풍경을 맛볼 수 있어요.   
    혼자만의 시간을 가지며 차분히 감정을 마주하기에 좋은 곳입니다.
     
    서울 여행 일정
    2025.12.11 - 2025.12.13(2박 3일)
    #감성 #미식 #여유 #힐링
      
    DAY1
    9:00 체크아웃
    호텔 서울스테이
    남산뷰 객실에서 여유로운 시작
     
    12:00 점심
    청춘떡볶이
    현지인이 추천하는 매콤한 떡복이와 튀김
     
    ...
    ...
     
    이런식으로 마지막 날까지 일정을 작성해줘. 
    """)
])

def recommend_place_by_emotion(emotion:str, place_list:list, res_list:list, days:str, companion_type:str) -> str:
    places_text = "\n".join([f"- {place}" for place in place_list])
    res_text = "\n".join([f"- {res}" for res in res_list])

    messages = template.format_messages(
        emotion=emotion,
        places=places_text,
        res=res_text,
        days=days,
        companion_type=companion_type
    )

    response = llm.invoke(messages)
    return response.content

# prompt = ChatPromptTemplate(input_variables=["query"], template=template)
llm = ChatOpenAI(temperature=0.8, max_tokens= 1024)

result = recommend_place_by_emotion(emotion, place_list, res_list,days, companion_type)
print(result)