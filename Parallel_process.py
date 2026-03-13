# add_data_parallel.py
# Optimized Parallel Sentiment Analysis
# Database: sen.db

import sqlite3
import concurrent.futures
import re
import os
import time
import multiprocessing

TEXT_FILE = "sample.txt"
DB_FILE = "sen.db"

POSITIVE_WORDS = {
    "good","great","happy","excellent","amazing",
    "awesome","nice","love","best","success",
    "positive","enjoy","wonderful","fantastic"
}

NEGATIVE_WORDS = {
    "bad","sad","terrible","awful","hate",
    "worst","poor","negative","failure",
    "problem","error","danger","critical"
}

ALERT_WORDS = {"error","fail","failure","danger","critical","warning"}

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
        print("Old database removed")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(CREATE_TABLE)

    conn.commit()
    conn.close()

    print("Database created")


def read_file():

    if not os.path.exists(TEXT_FILE):
        print("sample.txt not found")
        return ""

    with open(TEXT_FILE,"r",encoding="utf-8") as f:
        return f.read()


def split_sentences(text):

    sentences = re.split(r'[.!?]+', text)

    return [s.strip() for s in sentences if s.strip()]


def analyze_sentence(sentence):

    words = re.findall(r'\b\w+\b', sentence.lower())

    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)

    score = pos - neg

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

    return (
        sentence,
        sentiment,
        score,
        pos,
        neg,
        pattern,
        tag
    )


def main():

    start = time.time()

    setup_database()

    text = read_file()

    if not text:
        return

    sentences = split_sentences(text)

    print("Processing",len(sentences),"sentences")

    cpu_count = multiprocessing.cpu_count()

    workers = cpu_count * 2

    print("Using",workers,"threads")

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:

        results = list(executor.map(analyze_sentence, sentences))

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.executemany(INSERT_SQL, results)

    conn.commit()
    conn.close()

    end = time.time()

    print("All data stored in sen.db")

    print("Parallel Processing Time:", round(end-start,4),"seconds")


if __name__ == "__main__":
    main()