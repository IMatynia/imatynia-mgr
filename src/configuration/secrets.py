from pydantic import BaseModel


class Secrets(BaseModel):
    telegram_bot_api_key: str
    telegram_recipient_id: str
