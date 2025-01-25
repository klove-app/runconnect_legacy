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
    
    # Исправляем тип колонки log_id
    with engine.connect() as connection:
        try:
            # Изменяем тип колонки на SERIAL
            connection.execute(text("""
                DO $$ 
                BEGIN
                    -- Получаем максимальное значение
                    DECLARE max_id INTEGER;
                    SELECT COALESCE(MAX(log_id), 0) INTO max_id FROM running_log;
                    
                    -- Пересоздаем колонку как SERIAL
                    ALTER TABLE running_log ALTER COLUMN log_id DROP DEFAULT;
                    ALTER TABLE running_log ALTER COLUMN log_id SET DATA TYPE INTEGER;
                    CREATE SEQUENCE IF NOT EXISTS running_log_log_id_seq OWNED BY running_log.log_id;
                    ALTER TABLE running_log ALTER COLUMN log_id SET DEFAULT nextval('running_log_log_id_seq');
                    
                    -- Устанавливаем следующее значение
                    PERFORM setval('running_log_log_id_seq', max_id);
                END $$;
            """))
            connection.commit()
            logger.info("Running log ID column fixed successfully")
        except Exception as e:
            logger.error(f"Error fixing log_id column: {e}")
            raise 