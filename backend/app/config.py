from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:170599@localhost:5432/indianlaw"
    GEMINI_API_KEY =os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()