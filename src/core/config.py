from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, SecretStr, HttpUrl


class Settings(BaseSettings):
    dsn: PostgresDsn
    rabbitmq_url: str
    tg_webhook_url: str
    lolz_webhook_url: str
    heleket_webhook_url: str
    redis_url: str
    admin_ids: list[int]
    support_username: str
    remnawave_api_key: str
    remnawave_url_panel: str
    crypto_bot_token: str
    lolzteam_token: str
    secret_token: str
    bot_token: SecretStr
    merchant_id: str
    fernet_key: str
    heleket_send_payment_token: str
    heleket_get_invoices_token: str
    heleket_merchant_id: str
    guide_vpn_connect: HttpUrl
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
