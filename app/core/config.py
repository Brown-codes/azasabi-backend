from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sabi API"
    VERSION: str = "1.0.0"
    
    # We will use these later, but we set them up now
    GEMINI_API_KEY: str
    SUPABASE_DB_URL: str = ""

    # app/core/config.py (Add these below SUPABASE_DB_URL)
    SECRET_KEY: str = "default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()