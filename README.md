# Mockie 🚀

**Mockie** is a Python-based web application designed to help users prepare for interviews using automated resume parsing, NLP-powered evaluation, and mock interview simulations.

The project includes tools to analyze resumes, evaluate responses using natural language processing (NLP), and run interview sessions — all in one platform.

---

## 🔍 Features

- 📝 **Resume Parser** – Extracts and processes key details from user resumes.  
- 🤖 **Interview Engine** – Simulates interview questions and evaluates answers.  
- 🧠 **NLP Evaluator** – Assesses text responses using NLP.  
- 📊 **Confidence Detector** – Assigns confidence scores to responses.  
- 👔 **CV Analyzer** – Provides insights and quality feedback on resumes.  
- 🔐 **Authentication** – Secure login and registration system.  
- 🗃️ **Database Integration** – Stores user data and responses.  
- 💻 **Frontend** – Simple interface using HTML, CSS & JavaScript.

---

## 🧱 Project Structure

```text
mockie/
├── auth.py                    # Authentication routes
├── confidence_detector.py     # Confidence score logic
├── cv_analyzer.py             # Resume analysis logic
├── database.py                # Database connection & models
├── interview_engine.py        # Interview question logic
├── main.py                    # App entry point
├── nlp_evaluator.py           # NLP evaluation functions
├── resume_parser.py           # Resume parsing logic
├── static/                    # CSS and client assets
├── templates/                 # HTML templates (Flask/Jinja2)
├── requirements.txt           # Python dependencies
└── database.db                # SQLite database (example)
