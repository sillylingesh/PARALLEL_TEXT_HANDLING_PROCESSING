import sqlite3

db_path = r"d:\CODE BASE\PLAY GROUND\ling\PARALLEL_TEXT_HANDLING_PROCESSING\sen.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    with open("db_schema.txt", "w", encoding="utf-8") as f:
        f.write("--- SCHEMA ---\n")
        for name, sql in tables:
            f.write(f"Table: {name}\n")
            f.write(f"SQL: {sql}\n")
            f.write("-" * 20 + "\n")
            
        f.write("\n--- DATA ---\n")
        for name, _ in tables:
            cursor.execute(f"SELECT * FROM {name} LIMIT 5")
            rows = cursor.fetchall()
            f.write(f"Table {name} data:\n")
            for row in rows:
                f.write(str(row) + "\n")
            f.write("=" * 40 + "\n")
    conn.close()
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
