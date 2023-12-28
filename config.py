from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    URL: str
    FORMAT: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
