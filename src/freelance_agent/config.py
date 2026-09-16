from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    agent_api_key: str = "change-me"
    kaggle_username: str | None = None
    kaggle_api_token: str | None = None
    kaggle_worker_image: str | None = None
    kaggle_dataset: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
