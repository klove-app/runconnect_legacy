import sqlite3

def inspect_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== Структура базы данных ===\n")
    
    # Получить список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Таблица: {table_name}")
        print("------------------------")
        
        # Получить схему таблицы
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Вывести информацию о каждой колонке
        for column in columns:
            name = column[1]
            type_ = column[2]
            notnull = "NOT NULL" if column[3] else "NULL"
            pk = "PRIMARY KEY" if column[5] else ""
            print(f"- {name}: {type_} {notnull} {pk}")
            
        # Получить количество записей в таблице
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\nКоличество записей: {count}")
            
    conn.close()

if __name__ == "__main__":
    db_path = "/Users/ivankazakov/PycharmProjects/Runconnect_legacy/runconnect_legacy/running_bot.db"
    inspect_database(db_path) 