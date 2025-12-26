from pathlib import Path

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI SocketIO App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DEVICE_TOKEN_COOKIE_KEY:str = "device_token"


    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Security
    SECRET_KEY: str = "4YxmuoH80X6ApGoms2NAR7PRe0U_3Yfzh_9KenvOBDU="
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Socket.IO
    SOCKETIO_PATH: str = "/socket.io"
    SOCKETIO_CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database Config
    DB_HOST: str =  "localhost"
    DB_PORT: int =  5432
    DB_NAME: str =  "auth"

    # Credentials
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"

    # Providers
    DB_PROVIDER_MYSQL: str =  "mysql+pymysql"
    DB_PROVIDER_POSTGRES: str = "postgresql+psycopg"

    # Final database URI
    DATABASE_URI: str = (
        f"{DB_PROVIDER_POSTGRES}://"
        f"{DB_USER}:"
        f"{DB_PASS}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    UPLOAD_DIR: Path = Path(__file__).parent.parent.parent / "uploads"
    THUMB_DIR: Path = UPLOAD_DIR / "thumbnails"
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_WEBP_SIZE_KB: int = 10 * 1024
    ALLOWED_IMAGE_FORMATS: tuple = ("jpeg", "jpg", "png", "webp")
    ALLOWED_IMAGE_MIME_TYPES: list[str] = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
    THUMBNAIL_SIZE: tuple = (300, 300)  # width, height

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "delta-merchant"
    MINIO_SECURE: bool = False  # True if HTTPS

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()