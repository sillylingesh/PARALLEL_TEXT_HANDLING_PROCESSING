# add_data.py
# Advanced Sentiment Analysis with correct schema
# Database: sen.db

import sqlite3
import concurrent.futures
import threading
import queue
import re
import os

TEXT_FILE = "sample.txt"
DB_FILE = "sen.db"

# Word lists
POSITIVE_WORDS = {
    "good", "great", "happy", "excellent", "amazing",
    "awesome", "nice", "love", "best", "success",
    "positive", "enjoy", "wonderful", "fantastic"
}

NEGATIVE_WORDS = {
    "bad", "sad", "terrible", "awful", "hate",
    "worst", "poor", "negative", "failure",
    "problem", "error", "danger", "critical"
}

ALERT_WORDS = {"error", "fail", "failure", "danger", "critical", "warning"}

# CORRECT SCHEMA
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    score INTEGER NOT NULL,
    positive_count INTEGER NOT NULL,
    negative_count INTEGER NOT NULL,
    pattern TEXT NOT NULL,
    tag TEXT NOT NULL
);
"""

INSERT_SQL = """
INSERT INTO results (
    sentence,
    sentiment,
    score,
    positive_count,
    negative_count,
    pattern,
    tag
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""


# Create new DB and schema
def setup_database():

    # Delete old DB to avoid schema mismatch
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Old database removed.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(CREATE_TABLE)

    conn.commit()
    conn.close()

    print("New database sen.db created.")


# Read file
def read_file():

    if not os.path.exists(TEXT_FILE):
        print("sample.txt not found.")
        return ""

    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        return f.read()


# Split sentences
def split_sentences(text):

    sentences = re.split(r'[.!?]+', text)

    return [s.strip() for s in sentences if s.strip()]


# Sentiment calculation
def analyze_sentence(sentence):

    words = re.findall(r'\b\w+\b', sentence.lower())

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

    score = pos_count - neg_count

    if score > 0:
        sentiment = "POSITIVE"
    elif score < 0:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"

    # Pattern detection
    if "?" in sentence:
        pattern = "QUESTION"
    elif any(w in ALERT_WORDS for w in words):
        pattern = "ALERT"
    elif len(words) > 12:
        pattern = "LONG"
    else:
        pattern = "NORMAL"

    # Tagging
    if pattern == "ALERT":
        tag = "CRITICAL"
    elif score >= 2:
        tag = "VERY_POSITIVE"
    elif score <= -2:
        tag = "VERY_NEGATIVE"
    elif pattern == "QUESTION":
        tag = "QUERY"
    else:
        tag = sentiment

    return (
        sentence,
        sentiment,
        score,
        pos_count,
        neg_count,
        pattern,
        tag
    )


# Database writer thread
def db_writer(q):

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)

    cursor = conn.cursor()

    while True:

        data = q.get()

        if data is None:
            break

        try:
            cursor.execute(INSERT_SQL, data)
            conn.commit()
        except Exception as e:
            print("DB Error:", e)

        q.task_done()

    conn.close()


# Main
def main():

    setup_database()

    text = read_file()

    if not text:
        return

    sentences = split_sentences(text)

    print("Processing", len(sentences), "sentences...")

    write_queue = queue.Queue()

    writer = threading.Thread(target=db_writer, args=(write_queue,))
    writer.start()

    # Thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        futures = [executor.submit(analyze_sentence, s) for s in sentences]

        for future in concurrent.futures.as_completed(futures):

            write_queue.put(future.result())

    write_queue.join()

    write_queue.put(None)

    writer.join()

    print("All data stored in sen.db")


if __name__ == "__main__":
    main()
