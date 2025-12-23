import google.generativeai as genai
from config import GEMINI_API_KEY
from database import get_db_connection

# ================= GEMINI CONFIG =================
# SAFE + STABLE FOR FREE TIER

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-2.5-flash")

# ================= QUESTION GENERATION =================

def generate_question(
    interview_id: int,
    job_title: str,
    job_description: str = "",
    resume_text: str = ""
):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT question FROM questions WHERE interview_id = ?",
        (interview_id,)
    ).fetchall()
    conn.close()

    asked_questions = [r["question"] for r in rows]

    prompt = f"""
You are a senior technical interviewer.

JOB ROLE:
{job_title}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

PREVIOUS QUESTIONS:
{asked_questions}

RULES:
- Ask ONLY ONE interview question
- Question MUST be based on job description or resume
- Do NOT repeat previous questions
- Do NOT give answers
- Keep it professional

QUESTION:
"""

    response = MODEL.generate_content(prompt)
    return response.text.strip()

# ================= ANSWER EVALUATION =================

def evaluate_answer(question: str, answer: str):
    prompt = f"""
You are an interview evaluator.

QUESTION:
{question}

ANSWER:
{answer}

RULES:
- Score from 1 to 10
- Short feedback
- Do NOT rewrite answer

FORMAT:
Score: X
Feedback: <text>
"""

    response = MODEL.generate_content(prompt)
    return response.text.strip()
