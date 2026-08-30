"""
Central application configuration.

Reads settings from environment variables / a .env file so that
database credentials are never hard-coded in source code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()