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

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

# Gemini AI 추천 API(Pro버전 활용)
@app.get("/ai-recommend")
async def get_ai_recommend(
        weather: WeatherType = WeatherType.sunny,
        mood: MoodType = MoodType.happy,
        with_whom: CompanionType = CompanionType.alone
):

    prompt = (
        f"너는 전 세계 모든 요리를 섭렵한 최고의 푸드 큐레이터야.\n\n"
        f" [분석 데이터]\n"
        f" - 날씨: {weather.value}\n"
        f" - 사용자의 기분: {mood.value}\n"
        f" - 함께 먹는 사람: {with_whom.value}\n\n"
        f" [미션]\n"
        f" 위 3가지 요소를 심도 있게 분석해서, 지금 이 순간 사용자가 가장 행복하게 먹을 수 있는 점심 메뉴 딱 1가지만 추천해줘.\n"
        f" 한식, 중식, 일식, 양식, 에스닉 푸드 등 어떤 장르든 상관없어. 오직 '최고의 조합'에만 집중해.\n\n"
        f" [출력 형식]\n"
        f" 1. 첫 줄: 메뉴 이름 (예: 매콤한 해물 짬뽕)\n"
        f" 2. 두 번째 줄: 왜 이 메뉴가 현재 날씨와 기분, 그리고 동행자와의 상황에 완벽한 '인생 메뉴'인지 다정하고 설득력 있게 한 문장 설명해줘."
        )

    response = await model.generate_content_async(prompt)
    return {
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