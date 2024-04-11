import os


class Settings:
    DB_USERNAME = "admin"
    DB_PASSWORD = "admin"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "avito-test"
    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

    SECRET_KEY = os.getenv("SECRET_KEY", default="AWESOME_SECRET_KEY")  # JWT Secret key
    ALGORITHM = "HS256"  # JWT Algorithm


settings = Settings()
