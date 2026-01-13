from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/linkly"
    BASE_DOMAIN: str = "localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
