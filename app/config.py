from pydantic import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()