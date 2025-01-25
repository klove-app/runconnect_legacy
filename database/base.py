from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from database.logger import logger
from database.session import engine

# Создаем базовый класс для моделей
Base = declarative_base()
logger.info("Base model class created")

def init_db():
    """Инициализирует базу данных"""
    logger.info("Creating database tables...")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Сбрасываем последовательность для running_log_id
    with engine.connect() as connection:
        try:
            # Получаем максимальное значение log_id и устанавливаем последовательность
            connection.execute(text("""
                SELECT setval(pg_get_serial_sequence('running_log', 'log_id'), 
                            COALESCE((SELECT MAX(log_id) FROM running_log), 0) + 1);
            """))
            connection.commit()
            logger.info("Running log sequence reset successfully")
        except Exception as e:
            logger.error(f"Error resetting sequence: {e}")
            raise 