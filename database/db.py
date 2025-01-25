import psycopg2
from datetime import datetime, date
from config.config import DATABASE_URL
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_connection():
    """Создает и возвращает соединение с базой данных PostgreSQL"""
    try:
        # Парсим URL для получения параметров подключения
        url = urlparse(DATABASE_URL)
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def update_existing_runs_chat_id():
    """Обновляет chat_id для существующих записей о пробежках"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Обновляем chat_id для всех NULL записей, добавляя префикс -100
        cursor.execute("""
            UPDATE running_log 
            SET chat_id = '-1001487049035'
            WHERE chat_id IS NULL OR chat_id = '1487049035'
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        logger.info(f"Chat_id успешно обновлен для {affected_rows} существующих записей")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении chat_id: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def update_existing_runs_chat_type():
    """Обновляет chat_type для существующих записей о пробежках"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Обновляем chat_type для всех записей
        cursor.execute("""
            UPDATE running_log 
            SET chat_type = CASE
                WHEN chat_id IS NULL THEN 'private'
                ELSE 'group'
            END
            WHERE chat_type IS NULL
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        logger.info(f"Chat_type успешно обновлен для {affected_rows} существующих записей")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении chat_type: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def add_missing_columns():
    """Добавляет недостающие колонки в таблицы"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем наличие колонок в таблице running_log
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'running_log'
        """)
        columns = [column[0] for column in cursor.fetchall()]
        
        # Добавляем колонки в running_log
        if 'chat_type' not in columns:
            cursor.execute('ALTER TABLE running_log ADD COLUMN chat_type TEXT')
            logger.info("Добавлена колонка chat_type в таблицу running_log")
            update_existing_runs_chat_type()
            
        if 'chat_id' not in columns:
            cursor.execute('ALTER TABLE running_log ADD COLUMN chat_id TEXT')
            logger.info("Добавлена колонка chat_id в таблицу running_log")
            update_existing_runs_chat_id()
            
        if 'notes' not in columns:
            cursor.execute('ALTER TABLE running_log ADD COLUMN notes TEXT')
            logger.info("Добавлена колонка notes в таблицу running_log")
        
        # Проверяем наличие колонок в таблице users
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        columns = [column[0] for column in cursor.fetchall()]
        
        # Добавляем колонки в users
        if 'goal_km' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN goal_km FLOAT DEFAULT 0')
            logger.info("Добавлена колонка goal_km в таблицу users")
            
        if 'is_active' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true')
            logger.info("Добавлена колонка is_active в таблицу users")
            
        if 'chat_type' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN chat_type TEXT DEFAULT \'group\'')
            logger.info("Добавлена колонка chat_type в таблицу users")
        
        # Проверяем наличие колонок в таблице challenges
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'challenges'
        """)
        columns = [column[0] for column in cursor.fetchall()]
        
        # Добавляем колонки в challenges
        if 'chat_id' not in columns:
            cursor.execute('ALTER TABLE challenges ADD COLUMN chat_id TEXT')
            logger.info("Добавлена колонка chat_id в таблицу challenges")
            
        if 'is_system' not in columns:
            cursor.execute('ALTER TABLE challenges ADD COLUMN is_system BOOLEAN DEFAULT false')
            logger.info("Добавлена колонка is_system в таблицу challenges")
        
        conn.commit()
        logger.info("Структура базы данных успешно обновлена")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении структуры базы данных: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def check_tables_exist():
    """Проверяет существование необходимых таблиц"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем существование таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        # Проверяем наличие всех необходимых таблиц
        required_tables = {'users', 'running_log', 'challenges'}
        missing_tables = required_tables - set(existing_tables)
        
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            raise Exception(f"Required tables are missing: {missing_tables}")
            
        logger.info("All required tables exist")
        
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

# Проверяем таблицы при импорте модуля
check_tables_exist() 