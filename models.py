from datetime import datetime
import sqlite3

from pydantic import BaseModel

# 댓글 데이터를 주고받기 위한 규격
class FeedbackCreate(BaseModel):
    content: str

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 댓글 저장 함수
def save_feedback(content: str):
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO feedbacks (content, created_at) VALUES (?, ?)", (content, now))
    conn.commit()
    conn.close()

# 댓글 목록 가져오기 함수
def get_all_feedbacks():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT content, created_at FROM feedbacks ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"content": row[0], "date": row[1]} for row in rows]