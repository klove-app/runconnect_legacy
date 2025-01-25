from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database.logger import logger
from database.session import engine  # Импортируем engine здесь, чтобы избежать циклических зависимостей

# Создаем базовый класс для моделей
Base = declarative_base()
logger.info("Base model class created")

# Создаем локальную сессию для использования в обработчиках
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Local session factory created")

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