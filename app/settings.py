from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "PROKSIYAZILIM-BACKENDCASE"
    ENV: str = "dev"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DB_USER: str = "caseuser"
    DB_PASSWORD: str = "casepass"
    DB_NAME: str = "backend_case"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    DATABASE_URL: str | None = None  

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()