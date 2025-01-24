import psycopg2
import csv
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Using DATABASE_URL: {DATABASE_URL}")

def import_table(cursor, table_name):
    with open(f'{table_name}.csv', 'r') as f:
        reader = csv.reader(f)
        columns = next(reader)  # Читаем заголовки
        
        for row in reader:
            placeholders = ','.join(['%s'] * len(row))
            query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, row)

def import_all_data():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected successfully!")
        cursor = conn.cursor()
        
        tables = [
            'users',
            'running_log',
            'challenges',
            'challenge_participants',
            'teams',
            'team_members',
            'yearly_archive',
            'group_goals'
        ]
        
        for table in tables:
            try:
                print(f"Importing {table}...")
                import_table(cursor, table)
                print(f"Imported {table} successfully")
            except Exception as e:
                print(f"Error importing {table}: {e}")
                conn.rollback()
                continue
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    import_all_data()