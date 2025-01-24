import subprocess
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from config.config import DATABASE_URL

def wait_for_db():
    """Ждем пока база данных станет доступна"""
    engine = create_engine(DATABASE_URL)
    max_attempts = 30
    current_attempt = 0
    
    while current_attempt < max_attempts:
        try:
            # Пробуем подключиться к базе
            with engine.connect() as connection:
                print("Database is available!")
                return True
        except OperationalError:
            current_attempt += 1
            print(f"Database not available yet (attempt {current_attempt}/{max_attempts})")
            time.sleep(1)
    
    print("Could not connect to database")
    return False

def run_migrations():
    """Запускаем миграции"""
    try:
        # Переходим в директорию с миграциями
        subprocess.run(["cd", "runconnect_legacy"], check=True)
        
        # Запускаем миграции
        result = subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        if result.returncode == 0:
            print("Migrations completed successfully!")
            return True
        else:
            print("Migration failed!")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return False

if __name__ == "__main__":
    if wait_for_db():
        success = run_migrations()
        sys.exit(0 if success else 1)
    else:
        sys.exit(1) 