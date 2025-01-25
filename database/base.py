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
    
    # Создаем последовательность для running_log_id, если она не существует
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                DO $$ 
                BEGIN
                    CREATE SEQUENCE IF NOT EXISTS running_log_log_id_seq;
                    -- Получаем максимальное значение log_id
                    PERFORM setval('running_log_log_id_seq', COALESCE((SELECT MAX(log_id) FROM running_log), 0));
                END $$;
            """))
            connection.commit()
            logger.info("Sequence running_log_log_id_seq initialized")
        except Exception as e:
            logger.error(f"Error initializing sequence: {e}")
            raise
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully") 