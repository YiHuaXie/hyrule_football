from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OUHE_HTML_URL: str
    OUHE_API_URL: str
    OUHE_API_HOST: str
    REDIS_DEFAULT_URL: str
    LARK_APP_ID: str
    LARK_APP_SECRET: str
    DEEPSEEK_CHAT: str
    DEEPSEEK_API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
