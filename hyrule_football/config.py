from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ENV = os.getenv("APP_ENV", "dev")
env_file = ".env" if ENV == "release" else ".env.dev"


class Settings(BaseSettings):
    APP_ENV: str

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

    SQLITE_DB_URL: str

    MCP_SERVER_PORT: int = 8001
    MCP_SERVER_URL: str = "http://localhost:8001"  # 默认值，可通过环境变量覆盖

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        # 忽略 python_env/openai_api_key 等未在模型中声明的字段
        extra="ignore",
    )


settings = Settings()
