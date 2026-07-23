import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
CHANNEL_ID = os.getenv('CHANNEL_ID')
NOTIFY_CHANNEL_ID = os.getenv('NOTIFY_CHANNEL_ID') or CHANNEL_ID

if not TOKEN:
    raise ValueError("TOKEN не задан")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не задан")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не задан")