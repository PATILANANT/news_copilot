import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Vector Store
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./faiss_index")
    
    # Rate Limiting
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "1"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))

config = Config()