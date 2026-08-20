"""Application configuration loaded from environment variables (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "a_default_secret_key")
    DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
    TESTING = os.environ.get("TESTING", "False").lower() in ("true", "1")

    # Supabase Postgres connection string
    DATABASE_URI = os.environ.get(
        "DATABASE_URI",
        "postgresql://postgres.qsumfwhiianmrhkexlth:CNPMProject%402006@"
        "aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres",
    )

    JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", 8))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "uploads"))
    REPORT_FOLDER = os.environ.get("REPORT_FOLDER", os.path.join(os.path.dirname(__file__), "static", "reports"))
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB uploads
    CORS_HEADERS = "Content-Type"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


class FactoryConfig:
    @staticmethod
    def get_config(env: str):
        return {
            "development": DevelopmentConfig,
            "testing": TestingConfig,
            "production": ProductionConfig,
        }.get(env, DevelopmentConfig)


ENV = os.environ.get("FLASK_ENV", "development")
ActiveConfig = FactoryConfig.get_config(ENV)
