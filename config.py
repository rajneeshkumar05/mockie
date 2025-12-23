import os
from dotenv import load_dotenv

load_dotenv(".env.local")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
