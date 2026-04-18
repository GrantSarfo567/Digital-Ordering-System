from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 🔥 Get project root (03_backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str
    SUPABASE_PUBLISHABLE_KEY: str

    MTN_SUBSCRIPTION_KEY: str
    MTN_API_USER: str
    MTN_API_KEY: str

    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    model_config = {
        "env_file": os.path.join(BASE_DIR, ".env"),  # 🔥 FIX
        "case_sensitive": False
    }


settings = Settings()

