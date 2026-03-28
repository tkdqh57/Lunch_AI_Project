import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI
import random
import google.generativeai as genai
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from data import menu_db
from models import init_db, FeedbackCreate, save_feedback, get_all_feedbacks

# 1. API 키 불러오기
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Gemini 설정
genai.configure(api_key=api_key)

# 3. 모델 이름 수정 (중요: 앞의 'models/'를 빼고 적어보세요)
# 만약 그래도 안 되면 'gemini-1.5-flash-latest' 로 시도해 보세요.
model = genai.GenerativeModel('gemini-2.5-flash-lite')

app = FastAPI()

init_db()

class CompanionType(str, Enum):
    alone = "혼자"
    lover = "연인"
    friend = "친구"
    colleague = "직장동료"
    family = "가족"

class WeatherType(str, Enum):
    sunny = "맑음"
    rainy = "비"
    snowy = "눈"
    cloudy = "흐림"
    hot = "폭염"
    cold = "한파"

class MoodType(str, Enum):
    happy = "행복함"
    sad = "우울함"
    tired = "피곤함"
    hungry = "배고픔"
    diet = "다이어트 중"
    workout = "운동 완료! (단백질필요)"

class MenuCategory(str, Enum):
    korean = "한식"
    japanese = "일식"
    chinese = "중식"
    western = "양식"
    snack = "분식"      # 분식 추가!
    convenience = "편의점"
    random = "아무거나"

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

# Gemini AI 추천 API(Pro버전 활용)
@app.get("/ai-recommend")
async def get_ai_recommend(
        category: MenuCategory = MenuCategory.random,
        weather: WeatherType = WeatherType.sunny,
        mood: MoodType = MoodType.happy,
        with_whom: CompanionType = CompanionType.alone
):
    # AI에게 전달할 카테고리 설정
    category_text = f"'{category.value}' 종류중에서" if category != MenuCategory.random else "종류 상관없이 아무거나"

    prompt = (
        f"너는 미식 전문가야. 현재 상황은 날씨 '{weather.value}', 기분 '{mood.value}', 동행자 '{with_whom.value}'이야. "
        f"이 상황에 딱 맞는 점심 메뉴를 **{category_text}** 딱 1개만 추천해줘. "
        f"메뉴 이름과 함께, 왜 이 메뉴가 현재 카테고리와 상황에 베스트인지 다정한 말투로 한 문장 설명해줘."
        )

    response = await model.generate_content_async(prompt)
    return {
        "category": category.value,
        "weather": weather.value,
        "mood": mood.value,
        "with_whom": with_whom.value,
        "recommendation": response.text
    }

# 댓글 작성 API
@app.post("/feedback")
def create_feedback(feedback: FeedbackCreate):
    save_feedback(feedback.content)
    return {"message": "의견 감사합니다."}

# 댓글 목록 조회 API
@app.get("/feedbacks")
def get_feedback():
    return get_all_feedbacks()

# static 폴더를 "/" 경로로 연결 (index.html을 기본 화면으로 설정)
app.mount("/static", StaticFiles(directory="static"), name="static")