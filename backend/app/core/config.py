from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Telegestión de Luminarias"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/luminarias_db"
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
