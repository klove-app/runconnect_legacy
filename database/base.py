from sqlalchemy.ext.declarative import declarative_base
from database.logger import logger
from database.session import engine

# Создаем базовый класс для моделей
Base = declarative_base()
logger.info("Base model class created")

def init_db():
    """Инициализация базы данных"""
    logger.info("Initializing database")
    try:
        # Проверяем соединение с базой данных
        with engine.connect() as connection:
            logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise 