import sqlite3
import pandas as pd

db_path = r"d:\CODE BASE\PLAY GROUND\ling\PARALLEL_TEXT_HANDLING_PROCESSING\sen.db"
conn = sqlite3.connect(db_path)

# Get schema
cursor = conn.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("--- SCHEMA ---")
for name, sql in tables:
    print(f"Table: {name}")
    print(f"SQL: {sql}")
    print("-" * 20)

print("\n--- DATA ---")
for name, _ in tables:
    df = pd.read_sql_query(f"SELECT * FROM {name} LIMIT 5", conn)
    print(f"Table {name} data:")
    print(df)
    print("=" * 40)

conn.close()
