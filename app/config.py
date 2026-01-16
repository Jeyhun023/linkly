from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_DOMAIN: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
