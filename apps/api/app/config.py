from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    processing_enabled: bool = True
    admin_provider_token: str = ""
    database_url: str = "postgresql+psycopg://socialvid:localdevelopment@localhost:5432/socialvid"
    redis_url: str = "redis://localhost:6379/0"
    environment: Literal["development", "test", "production"] = "development"
    rate_limit_per_minute: int = Field(default=20, ge=1, le=1000)
    ip_hash_secret: str = "local-development-only"
    state_backend: Literal["redis", "sqlite"] = "sqlite"
    local_state_path: str = "/tmp/socialvid-state.sqlite"
    metadata_cache_ttl_seconds: int = 120
    max_storage_bytes: int = 1024 * 1024 * 1024
    extract_timeout_seconds: int = 90
    download_timeout_seconds: int = 180
    max_file_bytes: int = 200 * 1024 * 1024
    max_duration_seconds: int = 1800
    session_ttl_seconds: int = 600
    file_ttl_seconds: int = 600
    max_concurrent_jobs: int = 2
    ffprobe_path: str = "ffprobe"
    ffmpeg_path: str = "ffmpeg"
    media_root: str = "/tmp/socialvid-media"
    trusted_proxy_ips: str = "127.0.0.1,::1"
    allowed_hosts: str = "socialviddownloader.com,127.0.0.1,localhost,testserver,api"
    cors_origins: str = "https://socialviddownloader.com"

    @model_validator(mode="after")
    def validate_state_backend(self):
        if self.state_backend == "sqlite" and self.environment != "development":
            raise ValueError("SQLite state is available only in development")
        if self.environment == "production":
            if "*" in self.allowed_hosts or "*" in self.cors_origins:
                raise ValueError("Production hosts and CORS origins must be explicit")
            if len(self.ip_hash_secret) < 32 or self.ip_hash_secret in {"local-development-only", "replace-with-a-long-random-value"}:
                raise ValueError("Production requires a random IP_HASH_SECRET of at least 32 characters")
            if not self.database_url.startswith("postgresql") or "localdevelopment" in self.database_url:
                raise ValueError("Production requires PostgreSQL with non-development credentials")
            if self.admin_provider_token and len(self.admin_provider_token) < 32:
                raise ValueError("ADMIN_PROVIDER_TOKEN must contain at least 32 characters in production")
        for name in ("metadata_cache_ttl_seconds", "max_storage_bytes", "extract_timeout_seconds", "download_timeout_seconds",
                     "max_file_bytes", "max_duration_seconds", "session_ttl_seconds", "file_ttl_seconds", "max_concurrent_jobs"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.max_storage_bytes < self.max_file_bytes:
            raise ValueError("MAX_STORAGE_BYTES must cover at least one MAX_FILE_BYTES download")
        return self

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")


settings = Settings()
