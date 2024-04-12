import os


class Settings:
    DB_USERNAME = os.getenv("DB_USERNAME", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "avito-test")
    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", 0)
    REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", 1)

    SECRET_KEY = os.getenv("SECRET_KEY", default="AWESOME_SECRET_KEY")  # JWT Secret key
    ALGORITHM = "HS256"  # JWT Algorithm


settings = Settings()
