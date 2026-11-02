from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # Cloud database connection (Neon)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Local database fallback
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))
    DB_NAME = os.getenv("DB_NAME", "triallens")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local").lower()

settings = Settings()