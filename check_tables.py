from sqlalchemy import text
from runconnect_legacy.database.session import engine

with engine.connect() as conn:
    result = conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = \'public\';'))
    tables = sorted([row[0] for row in result])
    print("Существующие таблицы:")
    for table in tables:
        print(f"- {table}") 