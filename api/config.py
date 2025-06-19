from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_hostname: str = Field(..., alias="DATABASE_HOSTNAME")
    database_port: int = Field(..., alias="DATABASE_PORT")
    database_username: str = Field(..., alias="DATABASE_USERNAME")
    database_password: str = Field(..., alias="DATABASE_PASSWORD")
    database_name: str = Field(..., alias="DATABASE_NAME")
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(..., alias="ALGORITHM")
    access_token_expire_in_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_IN_MINUTES")
    refresh_token_expire_in_minutes: int = Field(..., alias="REFRESH_TOKEN_EXPIRE_IN_MINUTES")
    redis_hostname: str = Field(..., alias="REDIS_HOSTNAME")
    redis_port: int = Field(..., alias="REDIS_PORT")
    redis_db: int = Field(..., alias="REDIS_DB")
    maximum_failed_attempts: int = Field(..., alias="MAXIMUM_FAILED_ATTEMPTS")
    block_duration: int = Field(..., alias="BLOCK_DURATION")
    password_token_expire_in_minutes: int = Field(..., alias="PASSWORD_TOKEN_EXPIRE_IN_MINUTES")
    smtp_host: str = Field(..., alias="SMTP_HOST")
    smtp_port: int = Field(..., alias="SMTP_PORT")
    smtp_user: str = Field(..., alias="SMTP_USER")
    smtp_pass: str = Field(..., alias="SMTP_PASS")
    smtp_from: str = Field(..., alias="SMTP_FROM")


    class Config:
        env_file = ".env"

settings = Settings()
