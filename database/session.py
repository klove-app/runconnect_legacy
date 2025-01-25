from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.logger import logger
from config.config import DATABASE_URL

# Создаем URL для подключения к базе данных
SQLALCHEMY_DATABASE_URL = DATABASE_URL
logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

# Создаем движок базы данных с оптимальными параметрами для PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
logger.info("Database engine created")

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Session factory created")

# Создаем глобальную сессию для использования в моделях
Session = sessionmaker(bind=engine)
logger.info("Global session created")

def get_db():
    """Генератор сессий базы данных"""
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close() 