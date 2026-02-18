# view_data.py

import sqlite3

DB_FILE = "sen.db"

conn = sqlite3.connect(DB_FILE)

cursor = conn.cursor()

cursor.execute("SELECT * FROM results")

rows = cursor.fetchall()

print("\nID | Sentiment | Score | Pattern | Tag | Sentence")
print("-----------------------------------------------------------")

for row in rows:
    print(f"{row[0]} | {row[2]} | {row[3]} | {row[6]} | {row[7]} | {row[1]}")

conn.close()
