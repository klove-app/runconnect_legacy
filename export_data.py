import sqlite3
import csv
from datetime import datetime

def export_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Получаем имена колонок
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Записываем в CSV
    with open(f'{table_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

def export_all_data():
    conn = sqlite3.connect('running_bot.db')
    cursor = conn.cursor()
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"Exporting {table_name}...")
        export_table(cursor, table_name)
        print(f"Exported {table_name} successfully")
    
    conn.close()

if __name__ == "__main__":
    export_all_data()
