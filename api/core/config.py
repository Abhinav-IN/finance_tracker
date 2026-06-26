from api.utils.time import ist_now
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from api.utils.logger import create_info_logger

config_logger = create_info_logger("Configuration Logger")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding='utf-8')

    # Database Settings
    database_hostname: str = Field("localhost", alias="DATABASE_HOSTNAME")
    database_port: int = Field(5432, alias="DATABASE_PORT")
    database_username: str = Field("username", alias="DATABASE_USERNAME")
    database_password: str = Field("password", alias="DATABASE_PASSWORD")
    database_name: str = Field("finance_tracker", alias="DATABASE_NAME")

    # JWT Settings
    secret_key: str = Field("a_very_secret_key_that_should_be_long_and_random", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_in_minutes: int = Field(15, alias="ACCESS_TOKEN_EXPIRE_IN_MINUTES")

    # Authentication/Security Settings
    maximum_failed_attempts: int = Field(5, alias="MAXIMUM_FAILED_ATTEMPTS")
    block_duration: int = Field(3600, alias="BLOCK_DURATION")

    # Frontend base URL
    frontend_base_url: str = Field("https://fi-track.manavkashyap.com", alias="FRONTEND_BASE_URL")

    # Demo account
    demo_email: str = Field("test@gmail.com", alias="DEMO_EMAIL")

    # CORS Settings
    origins_string: str = Field(
        "http://localhost:3000,http://localhost:8000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:8000,http://fi-track.manavkashyap.com,https://fi-track.manavkashyap.com,http://127.0.0.1:5173,http://api-fi-track.manavkashyap.com,https://api-fi-track.manavkashyap.com,http://api-fi-track.manavkashyap.com:8000,https://api-fi-track.manavkashyap.com:8000",
        alias="ORIGINS",
    )

    @property
    def origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.origins_string.split(",") if origin.strip()]


ENV_FILE_PATH = ".env"
if not os.path.exists(ENV_FILE_PATH):
    config_logger.info(" Warning: .env file not found. Using environment variables.")

try:
    settings = Settings()
    config_logger.info(" Settings loaded successfully.")
    config_logger.info(f" Database Host: {settings.database_hostname}")
    config_logger.info(f" Secret Key (first 5 chars): {settings.secret_key[:5]}...")
    config_logger.info(f" Allowed Origins: {settings.origins}")
except Exception as e:
    config_logger.info(f" Error loading settings: {e}")
    exit(1)