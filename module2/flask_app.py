import os
import sqlite3
import re
from flask import Flask, render_template, request, g

app = Flask(__name__)

DB_FILE = "sen.db"

# Word lists from original script
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

INSERT_SQL = """
INSERT INTO results (
    sentence, sentiment, score, positive_count,
    negative_count, pattern, tag
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
        sentence, sentiment, score, pos_count,
        neg_count, pattern, tag
    )

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            # We assume a single sentence input for simplicity of UI
            result = analyze_sentence(text)
            
            # Save to DB
            db = get_db()
            cursor = db.cursor()
            cursor.execute(INSERT_SQL, result)
            db.commit()
            
            # Map tuple to dict for template
            result = {
                "sentence": result[0],
                "sentiment": result[1],
                "score": result[2],
                "pos_count": result[3],
                "neg_count": result[4],
                "pattern": result[5],
                "tag": result[6]
            }
            
    return render_template("index.html", result=result)

@app.route("/history")
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM results ORDER BY id DESC")
    rows = cursor.fetchall()
    return render_template("history.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
