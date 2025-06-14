from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_hostname: str = Field(..., alias="DATABASE_HOSTNAME")
    database_port: int = Field(..., alias="DATABASE_PORT")
    database_username: str = Field(..., alias="DATABASE_USERNAME")
    database_password: str = Field(..., alias="DATABASE_PASSWORD")
    database_name: str = Field(..., alias="DATABASE_NAME")

    class Config:
        env_file = ".env"

settings = Settings()
