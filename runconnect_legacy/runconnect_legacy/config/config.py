import os
from dotenv import load_dotenv
from pathlib import Path

# Получаем путь к текущей директории
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env файл
load_dotenv(BASE_DIR / '.env')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Bot
BOT_TOKEN = os.getenv('BOT_TOKEN') 