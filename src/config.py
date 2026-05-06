from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8338

    model_config = SettingsConfigDict(env_prefix="POLICY_SERVER_")


settings = Settings()
