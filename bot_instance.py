import os
from telebot import TeleBot
from config.config import BOT_TOKEN
from database.logger import logger

# Создаем экземпляр бота
logger.info("Creating bot instance")
logger.info(f"Bot token length: {len(BOT_TOKEN) if BOT_TOKEN else 'Token not found!'}")
bot = TeleBot(BOT_TOKEN, parse_mode='HTML')
logger.info("Bot instance created successfully")

# Проверяем подключение
try:
    bot_info = bot.get_me()
    logger.info(f"Bot connected successfully. Username: @{bot_info.username}")
except Exception as e:
    logger.error(f"Failed to connect to Telegram: {str(e)}")
    raise 