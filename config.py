import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Поддержка ID чата уведомлений или юзернейма канала
raw_channel = os.getenv("NOTIFY_CHANNEL_ID") or os.getenv("CHANNEL_ID")
try:
    NOTIFY_CHANNEL_ID = int(raw_channel)
except (ValueError, TypeError):
    NOTIFY_CHANNEL_ID = raw_channel

channel_env = os.getenv("CHANNEL_ID", "@channel")
CHANNEL_USERNAME = channel_env if channel_env.startswith("@") else "@channel"