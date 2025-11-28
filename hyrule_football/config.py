from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OUHE_HTML_URL: str
    OUHE_API_URL: str
    OUHE_API_HOST: str
    REDIS_DEFAULT_URL: str
    LARK_APP_ID: str
    LARK_APP_SECRET: str
    LARK_VERIFICATION_TOKEN: str
    DEEPSEEK_CHAT: str
    DEEPSEEK_API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 忽略 python_env/openai_api_key 等未在模型中声明的字段
        extra="ignore",
    )


settings = Settings()
