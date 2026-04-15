from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str
    SUPABASE_PUBLISHABLE_KEY: str

    MTN_SUBSCRIPTION_KEY: str
    MTN_API_USER: str
    MTN_API_KEY: str

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings()