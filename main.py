from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request,
    UploadFile,
    File,
    Form
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pathlib import Path
from fastapi import Request
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from database import init_db, get_db_connection
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from interview_engine import generate_question, evaluate_answer
from resume_parser import extract_text_from_pdf

# =====================================================
# APP INITIALIZATION
# =====================================================

app = FastAPI(title="AI Mock Interview App")

# =====================================================
# CORS (FIXES OPTIONS 405)
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # localhost dev
    allow_credentials=True,
    allow_methods=["*"],       # includes OPTIONS
    allow_headers=["*"],
)

# =====================================================
# STATIC FILES & TEMPLATES
# =====================================================

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =====================================================
# STARTUP
# =====================================================

@app.on_event("startup")
def startup():
    init_db()

# =====================================================
# SCHEMAS
# =====================================================

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AnswerRequest(BaseModel):
    interview_id: int
    question: str
    answer: str

# =====================================================
# BASIC ROUTES
# =====================================================

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# =====================================================
# AUTH ROUTES
# =====================================================

@app.post("/signup")
def signup(data: SignupRequest):
    conn = get_db_connection()

    if conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (data.email,)
    ).fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (data.name, data.email, hash_password(data.password))
    )
    conn.commit()
    conn.close()

    return {"message": "Signup successful"}


@app.post("/login")
def login(data: LoginRequest):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (data.email,)
    ).fetchone()
    conn.close()

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user["id"]})
    return {"access_token": token, "token_type": "bearer"}

# =====================================================
# HTML PAGES
# =====================================================

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/interview", response_class=HTMLResponse)
def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})


@app.get("/result", response_class=HTMLResponse)
def result_page(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})

# =====================================================
# INTERVIEW FLOW
# =====================================================

@app.post("/start-interview")
def start_interview(
    job_title: str = Form(None),
    job_description: str = Form(None),
    resume: UploadFile = File(None),
    current_user=Depends(get_current_user)
):
    resume_path = None

    if resume:
        resumes_dir = Path("resumes")
        resumes_dir.mkdir(exist_ok=True)
        resume_path = resumes_dir / f"{current_user['id']}_{resume.filename}"

        with open(resume_path, "wb") as f:
            f.write(resume.file.read())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO interviews (
        user_id,
        job_title,
        job_description,
        resume_path,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
""", (
    current_user["id"],
    job_title,
    job_description,
    str(resume_path) if resume_path else None,
    datetime.utcnow().isoformat()
))

    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"interview_id": interview_id}


@app.get("/next-question")
def next_question(interview_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()

    interview = conn.execute(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user["id"])
    ).fetchone()

    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")

    count = conn.execute(
        "SELECT COUNT(*) as total FROM questions WHERE interview_id = ?",
        (interview_id,)
    ).fetchone()["total"]

    if count >= 5:
        conn.close()
        return {"end": True}

    resume_text = None
    if interview["resume_path"]:
       resume_text = extract_text_from_pdf(interview["resume_path"])

    job_description = interview["job_description"]

    conn.close()

    question = generate_question(
    interview_id=interview_id,
    job_title=interview["job_title"],
    job_description=job_description,
    resume_text=resume_text
)


    return {
        "end": False,
        "question_number": count + 1,
        "question": question
    }


@app.post("/submit-answer")
def submit_answer(data: AnswerRequest, current_user=Depends(get_current_user)):
    evaluation = evaluate_answer(data.question, data.answer)

    score = int(
        [l for l in evaluation.splitlines() if "Score" in l][0].split(":")[1].strip()
    )
    feedback = (
        [l for l in evaluation.splitlines() if "Feedback" in l][0]
        .split(":", 1)[1]
        .strip()
    )

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO questions (interview_id, question, answer, score, feedback)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.interview_id,
            data.question,
            data.answer,
            score,
            feedback
        )
    )
    conn.commit()
    conn.close()

    return {"score": score, "feedback": feedback}

# =====================================================
# FINAL FEEDBACK
# =====================================================

@app.get("/final-feedback")
def final_feedback(interview_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT score FROM questions WHERE interview_id = ?",
        (interview_id,)
    ).fetchall()

    if not rows:
        conn.close()
        return {
            "summary": "No answers submitted. Score not available.",
            "score": 0
        }

    # ✅ Calculate average score from AVAILABLE answers (1 or more)
    avg_score = round(sum(r["score"] for r in rows) / len(rows), 1)

    if avg_score >= 7:
        result = "Good performance. Strong fundamentals."
    elif avg_score >= 5:
        result = "Average performance. Needs improvement."
    else:
        result = "Weak performance. Practice recommended."

    summary = f"Average Score: {avg_score}/10. {result}"

    # ✅ Save final score even if only 1 answer exists
    conn.execute(
        "UPDATE interviews SET final_score = ?, final_feedback = ? WHERE id = ?",
        (avg_score, summary, interview_id)
    )
    conn.commit()
    conn.close()

    return {
        "summary": summary,
        "score": avg_score
    }


# =====================================================
# INTERVIEW HISTORY
# =====================================================

@app.get("/my-interviews")
def my_interviews(current_user=Depends(get_current_user)):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, job_title, final_score, final_feedback, created_at
        FROM interviews
        WHERE user_id = ?
        AND final_score IS NOT NULL
        ORDER BY created_at DESC
    """, (current_user["id"],)).fetchall()
    conn.close()

    return [dict(r) for r in rows]


# =====================================================
# SKIP QUESTION HANDLER 
#===================================================

@app.post("/skip-question")
def skip_question(data: AnswerRequest, current_user=Depends(get_current_user)):
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO questions (interview_id, question, answer, score, feedback)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.interview_id,
            data.question,
            "",                       # no answer
            0,                        # score 0
            "Question skipped by candidate"
        )
    )

    conn.commit()
    conn.close()

    return {"message": "Question skipped"}

# =====================================================
# END INTERVIEW  
# ===================================================

@app.post("/end-interview")
def end_interview(interview_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()

    interview = conn.execute(
        "SELECT id FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user["id"])
    ).fetchone()

    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")

    # 🔥 Fetch all scores (even 1 answer)
    rows = conn.execute(
        "SELECT score FROM questions WHERE interview_id = ?",
        (interview_id,)
    ).fetchall()

    if rows:
        avg_score = round(sum(r["score"] for r in rows) / len(rows), 1)
        feedback = f"Average Score: {avg_score}/10"

        conn.execute(
            "UPDATE interviews SET final_score = ?, final_feedback = ? WHERE id = ?",
            (avg_score, feedback, interview_id)
        )
        conn.commit()

    conn.close()
    return {"message": "Interview ended", "final_score": avg_score if rows else 0}


# =====================================================
# GLOBAL OPTIONS HANDLER (BULLETPROOF)
# =====================================================


@app.options("/{path:path}")
def options_handler(path: str):
    return {}



@app.get("/start-interview", response_class=HTMLResponse)
def start_interview_page(request: Request):
    return templates.TemplateResponse(
        "interviewsetup.html",
        {"request": request}
    )



@app.get("/start-interview", response_class=HTMLResponse)
def interview_setup_page(request: Request):
    return templates.TemplateResponse(
        "interviewsetup.html",
        {"request": request}
    )

@app.get("/interview", response_class=HTMLResponse)
def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})




# =====================================================
# RECENT INTERVIEWS PAGE
# =====================================================
@app.get("/recent-interviews", response_class=HTMLResponse)
async def recent_interviews(request: Request):
    return templates.TemplateResponse(
        "recent_interviews.html",
        {"request": request}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
)

#=====================================================
# JOBS PAGE     
#====================================================
@app.get("/jobs", response_class=HTMLResponse)
async def jobs(request: Request):
    return templates.TemplateResponse(
        "jobs.html",
        {"request": request}
    )



#=================================================
# ai careers page
#====================================================

@app.get("/ai-careers", response_class=HTMLResponse)
async def ai_careers(request: Request):
    return templates.TemplateResponse(
        "ai_careers.html",
        {"request": request}
    )



#====================================================
# CV OPTIMIZATION PAGE
#====================================================

@app.get("/cv-optimization", response_class=HTMLResponse)
async def cv_optimization(request: Request):
    return templates.TemplateResponse(
        "cv_optimization.html",
        {"request": request}
    )


from cv_analyzer import analyze_resume

@app.post("/cv-optimization/analyze")
async def analyze_cv(
    resume: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    resumes_dir = Path("resumes")
    resumes_dir.mkdir(exist_ok=True)

    resume_path = resumes_dir / resume.filename
    with open(resume_path, "wb") as f:
        f.write(resume.file.read())

    text = extract_text_from_pdf(resume_path)
    result = analyze_resume(text)

    return result




# =====================================================
# PROFILE PAGE          
# =====================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # ✅ TEMP DUMMY USER (accept any token)
    return {
        "name": "Rajneesh Kumar",
        "email": "rk5677283@gmail.com",
        "role": "Student",
        "joined": "December 2025"
    }


@app.get("/me")
async def get_me(user=Depends(get_current_user)):
    return user


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse(
        "profile.html",
        {"request": request}
    )


# =====================================================
#support page
# ===================================================== 
@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse(
        "support.html",
        {"request": request}
    )

# ===================================================== 
#billing page
# ===================================================== 
@app.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request):
    return templates.TemplateResponse(
        "billing.html",
        {"request": request}
    )


















@app.get("/me")
async def get_me(user=Depends(get_current_user)):
    return {
        "name": user["name"],
        "email": user["email"]
    }





def get_current_user(token: str = Depends(oauth2_scheme)):
    # example mapping
    if token == "abc123":
        return {"name": "Nishant", "email": "nigesh@gmail.com"}

    raise HTTPException(status_code=401, detail="Invalid token")

# =====================================================
#FAVICON ROUTE
# ===================================================== 








from fastapi.responses import FileResponse

