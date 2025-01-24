import os
from telebot import TeleBot

# Получаем токен напрямую из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = TeleBot(BOT_TOKEN) 