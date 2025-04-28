from pydantic import BaseSettings, Field

class DbConfig(BaseSettings):
    host: str = Field(..., env="DB_HOST")
    port: int = Field(..., env="DB_PORT")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    name: str = Field(..., env="DB_NAME")

class TgBot(BaseSettings):
    token: str = Field(..., env="BOT_TOKEN")
    admin_ids: list[int] = Field(..., env="ADMIN_IDS")
    channel_id: str = Field(..., env="CHANNEL_ID")
    group_id: str = Field(..., env="GROUP_ID")

class QuotesApi(BaseSettings):
    url: str = Field(..., env="QUOTES_API_URL")
    key: str = Field(..., env="QUOTES_API_KEY")

class Config(BaseSettings):
    tg_bot: TgBot
    db: DbConfig
    quotes_api: QuotesApi

def load_config() -> Config:
    return Config(
        tg_bot=TgBot(),
        db=DbConfig(),
        quotes_api=QuotesApi()
    )