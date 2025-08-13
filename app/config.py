from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/bookstore_db"
    
    # Security Configuration
    secret_key: str = "your-secret-key-here-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Email Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # File Upload Configuration
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB in bytes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
