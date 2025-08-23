"""Configuration management for the CI/CD Fixer Agent."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://username:password@localhost:5432/cicd_fixer_db",
        env="DATABASE_URL"
    )
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="cicd_fixer_db", env="DATABASE_NAME")
    database_user: str = Field(default="username", env="DATABASE_USER")
    database_password: str = Field(default="password", env="DATABASE_PASSWORD")
    
    # GitHub Configuration
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_webhook_secret: str = Field(..., env="GITHUB_WEBHOOK_SECRET")
    
    # Google AI Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Portia Configuration
    portia_api_key: Optional[str] = Field(None, env="PORTIA_API_KEY")
    portia_environment: Optional[str] = Field(None, env="PORTIA_ENVIRONMENT")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/cicd_fixer.log", env="LOG_FILE")
    
    # Security Configuration
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Additional fields that might be set in environment
    api_key: Optional[str] = Field(None, env="API_KEY")
    frontend_url: Optional[str] = Field(None, env="FRONTEND_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings