"""
database.py — SQLite3 persistence layer
"""
import sqlite3
from datetime import datetime

DB_PATH = "text_processor.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS text_chunks (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id         TEXT,
            chunk_text       TEXT,
            sentiment_score  INTEGER,
            sentiment_label  TEXT,
            positive_count   INTEGER,
            negative_count   INTEGER,
            neutral_count    INTEGER,
            word_count       INTEGER,
            timestamp        TEXT
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_score ON text_chunks(sentiment_score)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_label ON text_chunks(sentiment_label)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_batch ON text_chunks(batch_id)')
    conn.commit()
    conn.close()


def insert_chunk(batch_id, chunk, score, label, pos, neg, neu, wc):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO text_chunks
            (batch_id, chunk_text, sentiment_score, sentiment_label,
             positive_count, negative_count, neutral_count, word_count, timestamp)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (batch_id, chunk, score, label, pos, neg, neu, wc,
          datetime.now().isoformat(timespec='seconds')))
    conn.commit()
    conn.close()


def fetch_all(search_keyword="", min_score=None, max_score=None, sentiment_filter="All"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = """SELECT id, chunk_text, sentiment_score, sentiment_label,
                  positive_count, negative_count, neutral_count, word_count, timestamp
           FROM text_chunks WHERE 1=1"""
    p = []
    if search_keyword:
        q += " AND chunk_text LIKE ?"
        p.append(f"%{search_keyword}%")
    if min_score is not None:
        q += " AND sentiment_score >= ?"
        p.append(min_score)
    if max_score is not None:
        q += " AND sentiment_score <= ?"
        p.append(max_score)
    if sentiment_filter and sentiment_filter != "All":
        q += " AND sentiment_label = ?"
        p.append(sentiment_filter)
    q += " ORDER BY id DESC"
    c.execute(q, p)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "chunk_text": r[1], "sentiment_score": r[2],
            "sentiment_label": r[3], "positive_count": r[4],
            "negative_count": r[5], "neutral_count": r[6],
            "word_count": r[7], "timestamp": r[8]
        }
        for r in rows
    ]


def get_aggregate_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*),
               AVG(sentiment_score),
               SUM(positive_count),
               SUM(negative_count),
               SUM(neutral_count),
               SUM(CASE WHEN sentiment_label='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment_label='Negative' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment_label='Neutral'  THEN 1 ELSE 0 END)
        FROM text_chunks
    """)
    row = c.fetchone()
    conn.close()
    if not row or not row[0]:
        return None
    return {
        "total": row[0],
        "avg_score": round(row[1] or 0, 2),
        "positive_words": row[2] or 0,
        "negative_words": row[3] or 0,
        "neutral_words": row[4] or 0,
        "positive_chunks": row[5] or 0,
        "negative_chunks": row[6] or 0,
        "neutral_chunks": row[7] or 0,
    }


def get_score_distribution():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sentiment_score FROM text_chunks ORDER BY id")
    scores = [r[0] for r in c.fetchall()]
    conn.close()
    return scores


def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM text_chunks")
    conn.commit()
    conn.close()