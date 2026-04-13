"""
Environment configuration and settings for OpenResQ backend.
All configuration is loaded from environment variables.
"""
import os
import json
import logging
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pydantic_settings import SettingsConfigDict

logger = logging.getLogger(__name__)


def _read_env_value_from_file(key: str, env_file: str = ".env") -> Optional[str]:
    """Best-effort fallback reader for simple KEY=VALUE entries in .env."""
    try:
        if not os.path.exists(env_file):
            return None

        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                k, v = stripped.split("=", 1)
                if k.strip() == key:
                    return v.strip()
    except Exception:
        return None
    return None


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
    
    # OpenAI
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() in ["production", "prod"]
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() in ["development", "dev", "local"]
    
    def get_firebase_credentials(self) -> dict:
        """Load Firebase credentials from environment variable."""
        raw_value = (
            self.firebase_credentials_json
            or os.getenv("FIREBASE_CREDENTIALS")
            or _read_env_value_from_file("FIREBASE_CREDENTIALS", ".env")
            or _read_env_value_from_file("FIREBASE_CREDENTIALS", "backend/.env")
        )

        # Some .env files wrap the JSON value in single/double quotes.
        if raw_value and len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in ("'", '"'):
            raw_value = raw_value[1:-1]

        if not raw_value:
            raise ValueError(
                "FIREBASE_CREDENTIALS environment variable not set. "
                "Please provide Firebase service account JSON as a base64-encoded string or raw JSON."
            )
        
        try:
            # Try parsing as JSON directly
            return json.loads(raw_value)
        except json.JSONDecodeError:
            try:
                # Try base64 decoding if JSON parsing fails
                import base64
                decoded = base64.b64decode(raw_value).decode('utf-8')
                return json.loads(decoded)
            except Exception as e:
                logger.error(f"Failed to parse Firebase credentials: {e}")
                raise ValueError("Invalid FIREBASE_CREDENTIALS format")


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
