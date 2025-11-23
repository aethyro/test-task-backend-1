from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field("Project", alias="APP_NAME")
    debug: bool = Field(False, alias="DEBUG")
    logging_level: str = Field("INFO", alias="LOGGING_LEVEL")

    db_schema: str = Field(default="postgres", alias="DB_SCHEME")
    db_host: str = Field(default="db", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_database: str = Field(default="db", alias="DB_DATABASE")
    db_user: str = Field(default="admin", alias="DB_USER")
    db_password: str = Field(default="admin", alias="DB_PASSWORD")

    @computed_field
    @property
    def db_dsn(self) -> str:
        if self.db_schema.startswith("sqlite"):
            return f"{self.db_schema}://{self.db_database}"

        return (
            f"{self.db_schema}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_database}"
        )

    @computed_field
    @property
    def adb_dsn(self) -> str:
        return (
            f"{self.db_schema}+asyncpg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
