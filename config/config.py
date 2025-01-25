import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
# Убедимся, что используется правильный префикс для PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")
ADMIN_IDS = os.getenv('ADMIN_IDS', '1431390352').split(',')

# Настройки Stability AI
STABILITY_API_HOST = 'https://api.stability.ai'
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
STABLE_DIFFUSION_ENGINE_ID = 'stable-diffusion-xl-1024-v1-0'

# Настройки веб-сервера
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '0.0.0.0')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')

# Режим работы (polling или webhook)
BOT_MODE = os.getenv('BOT_MODE', 'polling')  # или 'webhook' 
