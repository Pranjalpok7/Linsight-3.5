import os 
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TAVILY_API_KEY or not GOOGLE_API_KEY:
    raise ValueError(f"TAVILY_API_KEY and GOOGLE_API_KEY not found in environment"
    f"variables")
    