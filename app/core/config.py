from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    frontend_url: str


settings = Settings()