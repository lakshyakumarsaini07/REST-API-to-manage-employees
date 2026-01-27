from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    secret_key: str = Field(alias="SECRET_KEY")

    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    api_title: str = Field(default="Employee Management API", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    api_description: str = Field(
        default="A robust REST API for employee management",
        alias="API_DESCRIPTION"
    )

    password_min_length: int = Field(default=8, alias="PASSWORD_MIN_LENGTH")

    model_config = SettingsConfigDict(
        env_file=".env",
        populate_by_name=True,
        extra="forbid"
    )

settings = Settings()
