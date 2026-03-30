import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI
import google.generativeai as genai
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

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

class GenderType(str, Enum):
    male = "남성"
    female = "여성"
    none = "선택안함"

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
        gender: GenderType = GenderType.none,
        weather: WeatherType = WeatherType.sunny,
        mood: MoodType = MoodType.happy,
        with_whom: CompanionType = CompanionType.alone,
        additional_request: str = ""
):
    gender_text = f"성별은 '{gender.value}'이고 " if gender != GenderType.none else ""

    request_text = f"\n [사용자의 특별 요청]\n - \"{additional_request}\"" if additional_request else ""

    prompt = (
        f"너는 사용자의 취향과 상황을 완벽하게 파악하는 미식 큐레이터야.\n\n"
        f" [기본 데이터]\n"
        f" - 사용자 정보: {gender_text}'{with_whom.value}'와(과) 함께 식사 예정\n"
        f" - 환경 데이터: 날씨 '{weather.value}', 기분 '{mood.value}'{request_text}\n\n"
        f" [미션]\n"
        f" 위 데이터를 종합 분석해서 지금 이 순간 사용자에게 가장 감동을 줄 수 있는 점심 메뉴 1가지만 추천해줘. "
        f"특히 사용자의 특별 요청 사항이 있다면 이를 최우선으로 반영해줘.\n\n"
        f" [출력 형식]\n"
        f" 1. 첫 줄: 메뉴 이름\n"
        f" 2. 두 번째 줄: 추천 이유 설명"
        )

    response = await model.generate_content_async(prompt)
    return {
        "weather": weather.value,
        "mood": mood.value,
        "with_whom": with_whom.value,
        "recommendation": response.text,
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