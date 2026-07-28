import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Приватный канал для уведомлений (куда падают заявки)
raw_notify = os.getenv("NOTIFY_CHANNEL_ID")
NOTIFY_CHANNEL_ID = int(raw_notify) if raw_notify and raw_notify.lstrip("-").isdigit() else raw_notify

# Публичный канал для проверки подписки пользователей
CHANNEL_USERNAME = os.getenv("CHANNEL_ID", "@jgsjgjjgd")