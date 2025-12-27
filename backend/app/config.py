"""
Environment configuration and settings for OpenResQ backend.
All configuration is loaded from environment variables.
"""
import os
import json
import logging
from pydantic import BaseSettings, Field
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings     loaded from environment variables."""
    
    # Application
    app_name: str = "OpenResQ"
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Firebase
    firebase_project_id: str = Field(env="FIREBASE_PROJECT_ID")
    firebase_storage_bucket: str = Field(env="FIREBASE_STORAGE_BUCKET")
    firebase_credentials_json: Optional[str] = Field(default=None, env="FIREBASE_CREDENTIALS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_write_per_hour: int = Field(default=100, env="RATE_LIMIT_WRITE_PER_HOUR")
    
    # Database (if needed for gradual migration)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Logging
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    ws_auth_required: bool = Field(default=True, env="WS_AUTH_REQUIRED")
    
    # Deployment
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() in ["production", "prod"]
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() in ["development", "dev", "local"]
    
    def get_firebase_credentials(self) -> dict:
        """Load Firebase credentials from environment variable."""
        if not self.firebase_credentials_json:
            raise ValueError(
                "FIREBASE_CREDENTIALS environment variable not set. "
                "Please provide Firebase service account JSON as a base64-encoded string or raw JSON."
            )
        
        try:
            # Try parsing as JSON directly
            return json.loads(self.firebase_credentials_json)
        except json.JSONDecodeError:
            try:
                # Try base64 decoding if JSON parsing fails
                import base64
                decoded = base64.b64decode(self.firebase_credentials_json).decode('utf-8')
                return json.loads(decoded)
            except Exception as e:
                logger.error(f"Failed to parse Firebase credentials: {e}")
                raise ValueError("Invalid FIREBASE_CREDENTIALS format")


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
