"""Enhanced configuration module using Pydantic BaseSettings.

This extends config.py with validated settings from .env files.
"""

from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older Pydantic versions
    from pydantic import BaseSettings

from pydantic import Field

from config import (
    APP_NAME,
    APP_VERSION,
    DATA_DIR,
    ANALYSES_DIR,
)


class AppSettings(BaseSettings):
    """Application settings with Pydantic validation and .env support.

    Features:
    - Automatic .env file loading
    - Type validation
    - Environment variable overrides
    - Documented fields with defaults

    Usage:
        from config_pydantic import app_settings
        print(app_settings.api_port)  # 3000
        print(app_settings.aws_region)  # us-east-1
    """

    # Environment
    janus_env: str = Field(default="development", description="Runtime environment")
    janus_verbose: bool = Field(default=False, description="Verbose logging")
    janus_cache: bool = Field(default=True, description="Cache results")
    janus_use_mock: bool = Field(default=False, description="Use mock AWS Q")

    # AWS
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_builder_id_email: str = Field(default="", description="AWS Builder ID email")

    # Server
    api_host: str = Field(default="127.0.0.1", description="API host")
    api_port: int = Field(default=3000, description="API port")
    frontend_host: str = Field(default="127.0.0.1", description="Frontend host")
    frontend_port: int = Field(default=5173, description="Frontend port")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="CORS origins (comma-separated)",
    )

    # Amazon Q
    amazon_q_timeout: int = Field(default=60, description="AWS Q timeout (seconds)")
    amazon_q_retries: int = Field(default=3, description="AWS Q retry attempts")
    amazon_q_backoff: float = Field(default=2.0, description="Exponential backoff")

    # Logging
    log_level: str = Field(default="DEBUG", description="Log level")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list."""
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if production environment."""
        return self.janus_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if development environment."""
        return self.janus_env == "development"


# Create global settings instance (validates .env on import)
app_settings = AppSettings()
