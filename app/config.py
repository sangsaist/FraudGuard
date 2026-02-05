import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
