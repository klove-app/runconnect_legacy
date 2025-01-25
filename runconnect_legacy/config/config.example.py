import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@host:port/dbname')

# Bot
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token_here')
TOKEN = BOT_TOKEN  # для обратной совместимости
ADMIN_IDS = os.getenv('ADMIN_IDS', '1234567890').split(',')

# Настройки Stability AI
STABILITY_API_HOST = 'https://api.stability.ai'
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY', 'your_stability_api_key_here')
STABLE_DIFFUSION_ENGINE_ID = 'stable-diffusion-xl-1024-v1-0'

# Настройки логирования
LOG_FILE = 'bot.log'
LOG_LEVEL = 'INFO'

# Максимальные значения
MAX_DISTANCE = 100  # максимальная дистанция для одной пробежки в км
MAX_GOAL = 100000  # максимальная годовая цель в км 