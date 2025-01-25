from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

# Создаем логгер
logger = logging.getLogger(__name__)

from config.config import DATABASE_URL

# Создаем URL для подключения к базе данных
SQLALCHEMY_DATABASE_URL = DATABASE_URL
logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

# Создаем движок базы данных с настройками для PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # проверка соединения перед использованием
    pool_size=5,  # размер пула соединений
    max_overflow=10  # максимальное количество дополнительных соединений
)
logger.info("Database engine created")

# Создаем фабрику сессий
Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
logger.info("Session factory created")

def get_db():
    """Генератор сессий базы данных"""
    logger.debug("Creating new database session")
    db = Session()
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()

logger.info("Database session configuration complete") 