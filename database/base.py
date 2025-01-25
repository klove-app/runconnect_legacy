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
    
    # Пересоздаем последовательность для running_log_id
    with engine.connect() as connection:
        try:
            # Удаляем старую последовательность, если она существует
            connection.execute(text("""
                DO $$ 
                BEGIN
                    -- Удаляем привязку последовательности к колонке
                    ALTER TABLE running_log ALTER COLUMN log_id DROP DEFAULT;
                    
                    -- Удаляем старую последовательность, если она существует
                    DROP SEQUENCE IF EXISTS running_log_log_id_seq;
                    
                    -- Создаем новую последовательность
                    CREATE SEQUENCE running_log_log_id_seq;
                    
                    -- Устанавливаем следующее значение после максимального
                    PERFORM setval('running_log_log_id_seq', COALESCE((SELECT MAX(log_id) FROM running_log), 0));
                    
                    -- Привязываем последовательность к колонке
                    ALTER TABLE running_log ALTER COLUMN log_id 
                    SET DEFAULT nextval('running_log_log_id_seq');
                END $$;
            """))
            connection.commit()
            logger.info("Running log sequence recreated successfully")
        except Exception as e:
            logger.error(f"Error recreating sequence: {e}")
            raise 