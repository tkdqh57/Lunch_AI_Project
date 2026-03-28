import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI
import random
import google.generativeai as genai

from data import menu_db

# .env 파일로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("GEMINI_API_KEY")

# Gemini 설정 (발급받은 API 키 입력)
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

app = FastAPI()

class CompanionType(str, Enum):
    alone = "혼자",
    lover = "연인",
    friend = "친구",
    colleague = "직장동료",
    family = "가족"

class WeatherType(str, Enum):
    sunny = "맑음",
    rainy = "비",
    snowy = "눈",
    cloudy = "흐림",
    hot = "폭염",
    cold = "한파"

class MoodType(str, Enum):
    happy = "행복함",
    sad = "우울함",
    tired = "피곤함",
    hungry = "배고픔",
    diet = "다이어트 중",
    workout = "운동 완료! (단백질필요)"

@app.get("/")
def read_root():
    return{"message": "오늘 뭐 먹지? 에 오신것을 환영합니다."}


# 단순 랜덤 추천 API
@app.get("/recommend/{category}")
def get_random_menu(category: str):
    if category in menu_db:
        selection = random.choice(menu_db[category])
        return {"category": category, "menu": selection, "type": "random"}

    available_categories = list(menu_db.keys())
    return {
        "error": f"카테고리를 찾을 수 없습니다. 선택가능: {', '.join(available_categories)}"
    }

# Gemini AI 추천 API(Pro버전 활용)
@app.get("/ai-recommend")
async def get_ai_recommend(
        weather: WeatherType = WeatherType.sunny,
        mood: MoodType = MoodType.happy,
        with_whom: CompanionType = CompanionType.alone
):

    prompt = (
        f"너는 지금 나({with_whom.value}와 함께 있는 상태)의 점심 메뉴를 골라주는 다정한 친구나 연인이야."
        f"오늘 날씨는 {weather.value}이고 내 기분은 {mood.value}이야."
        f"특히 지금 내가 **{with_whom.value}**와(과) 함께 밥을 먹으러 가야 한다는 점을 꼭 고려해줘"
        f"이 상황에 가장 센스 있는 메뉴 1개를 추천해주고"
        f"왜 그 메뉴가 {with_whom.value}와(과) 먹기에 좋은지 다정한 말투로 한 문장으로 말해줘."
        )

    response = await model.generate_content_async(prompt)
    return {
        "weather": weather.value,
        "mood": mood.value,
        "with_whom": with_whom.value,
        "recommendation": response.text,
        "type": "ai_context_recommend"
    }