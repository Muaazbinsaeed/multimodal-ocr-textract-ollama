from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Ollama configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llava"
    request_timeout_ms: int = 60000

    # File upload limits
    max_upload_mb: int = 10
    allowed_image_mime: str = "image/png,image/jpeg,image/webp"

    # CORS configuration
    allowed_origins: str = "http://localhost:8080,http://localhost:3000"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def max_upload_bytes(self) -> int:
        """Convert max upload MB to bytes"""
        return self.max_upload_mb * 1024 * 1024

    @property
    def allowed_mime_types(self) -> list[str]:
        """Convert comma-separated MIME types to list"""
        return [mime.strip() for mime in self.allowed_image_mime.split(",")]

    @property
    def cors_origins(self) -> list[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def request_timeout_seconds(self) -> float:
        """Convert timeout from milliseconds to seconds"""
        return self.request_timeout_ms / 1000.0


# Global settings instance
settings = Settings()