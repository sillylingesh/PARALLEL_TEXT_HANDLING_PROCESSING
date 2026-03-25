# add_data.py
# Sequential Sentiment Analysis (No Parallel Processing)
# Database: sen.db

import sqlite3
import re
import os
import time

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


def setup_database():

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Old database removed.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(CREATE_TABLE)

    conn.commit()
    conn.close()

    print("New database sen.db created.")


def read_file():

    if not os.path.exists(TEXT_FILE):
        print("sample.txt not found.")
        return ""

    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def split_sentences(text):

    sentences = re.split(r'[.!?]+', text)

    return [s.strip() for s in sentences if s.strip()]


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

    if "?" in sentence:
        pattern = "QUESTION"
    elif any(w in ALERT_WORDS for w in words):
        pattern = "ALERT"
    elif len(words) > 12:
        pattern = "LONG"
    else:
        pattern = "NORMAL"

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
    time.sleep(0.001)
    return (
        sentence,
        sentiment,
        score,
        pos_count,
        neg_count,
        pattern,
        tag
    )


def main():

    start_time = time.time()   # Start time

    setup_database()

    text = read_file()

    if not text:
        return

    sentences = split_sentences(text)

    print("Processing", len(sentences), "Sentences...")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Sequential processing
    for sentence in sentences:

        result = analyze_sentence(sentence)

        cursor.execute(INSERT_SQL, result)

    conn.commit()
    conn.close()

    end_time = time.time()   # End time

    print("All data stored in sen.db")
    print("Sequential Processing Time:", round(end_time - start_time, 4), "seconds")


if __name__ == "__main__":
    main()