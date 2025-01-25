import os
from telebot import TeleBot
from config.config import BOT_TOKEN, logger

# Создаем экземпляр бота
logger.info("Creating bot instance")
bot = TeleBot(BOT_TOKEN, parse_mode='HTML')
logger.info("Bot instance created successfully") 