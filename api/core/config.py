from api.utils.time import ist_now
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from datetime import datetime 
from api.utils.logger import create_info_logger

config_logger = create_info_logger("Configuration Logger")

def get_timestamp():
    return ist_now().strftime("[%Y-%m-%d %H:%M:%S]")

class Settings(BaseSettings):
    config_logger.info(f" Please Wait, Loading Settings")


    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding='utf-8')

    print("-----------------------------------------------")
    
    # Database Settings
    config_logger.info(f" Loading Database Information")
    database_hostname: str = Field("localhost", alias="DATABASE_HOSTNAME")
    database_port: int = Field(5432, alias="DATABASE_PORT")
    database_username: str = Field("username", alias="DATABASE_USERNAME")
    database_password: str = Field("password", alias="DATABASE_PASSWORD") # IMPORTANT: Change this in production!
    database_name: str = Field("finance_tracker", alias="DATABASE_NAME")
    config_logger.info(f" Database Information loaded")
    print("-----------------------------------------------")

    # JWT Settings
    config_logger.info(f" Loading JWT Token Information")
    secret_key: str = Field("a_very_secret_key_that_should_be_long_and_random", alias="SECRET_KEY") # IMPORTANT: Change this in production!
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_in_minutes: int = Field(15, alias="ACCESS_TOKEN_EXPIRE_IN_MINUTES")
    config_logger.info(f" JWT Token Information Loaded Successfully")
    print("-----------------------------------------------")

    # Redis Settings
    config_logger.info(f" Loading Redis Information")
    redis_hostname: str = Field("localhost", alias="REDIS_HOSTNAME")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    config_logger.info(f" Redis Information Loaded")
    print("-----------------------------------------------")



    # Authentication/Security Settings
    config_logger.info(f" Loading Authentication/Security Settings")
    maximum_failed_attempts: int = Field(5, alias="MAXIMUM_FAILED_ATTEMPTS")
    block_duration: int = Field(3600, alias="BLOCK_DURATION") # seconds (e.g., 1 hour)
    password_token_expire_in_minutes: int = Field(15, alias="PASSWORD_TOKEN_EXPIRE_IN_MINUTES")
    verification_token_expire_in_minutes: int = Field(30, alias="VERIFICATION_TOKEN_EXPIRE_IN_MINUTES")
    config_logger.info(f" Authentication/Security Settings Loaded Fully")
    print("-----------------------------------------------")

    # SMTP (Email) Settings
    config_logger.info(f" Loading SMTP (Email) Settings")
    smtp_host: str = Field("smtp.mailtrap.io", alias="SMTP_HOST") # Example for mailtrap
    smtp_port: int = Field(2525, alias="SMTP_PORT")
    smtp_user: str = Field("your_smtp_username", alias="SMTP_USER")
    smtp_pass: str = Field("your_smtp_password", alias="SMTP_PASS")
    smtp_from: str = Field("no-reply@yourdomain.com", alias="SMTP_FROM")
    config_logger.info(f" SMTP (Email) Settings Loaded Fully")
    print("-----------------------------------------------")

    # Google Gemini settings
    config_logger.info(f" Loading Google Gemini Settings")
    google_gemini_api_key: str = Field("gemini_api_key", alias="GEMINI_API_KEY") 

    
    # CORS Settings
    config_logger.info(f" Loading CORS Settings/Information")
    origins_string: str = Field("http://localhost:3000,http://localhost:8000,http://localhost:5173/", alias="ORIGINS")
    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.origins_string.split(',') if origin.strip()]
    
    config_logger.info(f" CORS Settings Loaded Fully")
    print("-----------------------------------------------")


# --- Logic to check for .env file and instantiate settings ---
ENV_FILE_PATH = ".env"

if not os.path.exists(ENV_FILE_PATH):
    config_logger.info(f" Warning: .env file not found at '{ENV_FILE_PATH}'. "
          "Using default settings or environment variables.")
    # You might want to raise an exception here for production environments
    # raise FileNotFoundError(f".env file not found at '{ENV_FILE_PATH}'. Please create it.")

try:
    settings = Settings()
    print("************************************************")
    config_logger.info(f" Settings loaded successfully.")
    config_logger.info(f" Database Host: {settings.database_hostname}")
    config_logger.info(f" Secret Key (first 5 chars): {settings.secret_key[:5]}...")
    config_logger.info(f" Allowed Origins: {settings.origins}")
except Exception as e:
    config_logger.info(f" Error loading settings: {e}")
    config_logger.info(f" Ensure all required environment variables are set or have default values.")
    exit(1) # Exit if settings cannot be loaded
