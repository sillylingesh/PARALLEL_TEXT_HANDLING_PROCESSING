# 🚀 Parallel Rule-Based Sentiment Analysis System

### 🧠 Python + SQLite + Multithreading

---

## 📌 Project Description

The **Parallel Rule-Based Sentiment Analysis System** is a Python application that analyzes text files, calculates sentiment scores, detects patterns, tags content, and stores results in a SQLite database using **parallel processing (ThreadPool)**.

This project demonstrates:

* ⚡ Parallel processing
* 🧵 Multithreading
* 🗄️ SQLite database integration
* 🧠 Rule-based NLP
* 📊 Structured data storage

---

## 🖼️ System Architecture

![System Architecture](architecture.png)

```
           sample.txt
               │
               ▼
      Sentence Splitter
               │
               ▼
     ThreadPool Executor
   ┌─────────┬─────────┬─────────┐
   ▼         ▼         ▼         ▼
Sentence  Sentence  Sentence  Sentence
Analyzer  Analyzer  Analyzer  Analyzer
   │         │         │         │
   └─────────┴─────────┴─────────┘
               │
               ▼
        Database Writer Thread
               │
               ▼
            sen.db
               │
               ▼
         view_data.py
```

---

## ✨ Features

### ⚙️ Core Features

* 📄 Automatic text file reading
* ✂️ Sentence splitting
* 😊 Positive sentiment detection
* 😡 Negative sentiment detection
* ⚖️ Sentiment score calculation
* 🔍 Pattern detection
* 🏷️ Content tagging
* 🧵 Multithreading processing
* ⚡ ThreadPool parallel execution
* 🗄️ SQLite database storage
* 👁️ Database viewer

---

### 🧠 Sentiment Logic

| Condition                       | Result      |
| ------------------------------- | ----------- |
| Positive words > Negative words | 😊 POSITIVE |
| Negative words > Positive words | 😡 NEGATIVE |
| Equal words                     | 😐 NEUTRAL  |

---

### 🔍 Pattern Detection

| Pattern    | Detection                       |
| ---------- | ------------------------------- |
| QUESTION ❓ | Sentence contains "?"           |
| ALERT ⚠️   | Contains error, failure, danger |
| LONG 📏    | Sentence length > 12 words      |
| NORMAL ✅   | Default                         |

---

### 🏷️ Tagging System

| Tag              | Meaning             |
| ---------------- | ------------------- |
| VERY_POSITIVE 🌟 | High positive score |
| VERY_NEGATIVE 🔥 | High negative score |
| CRITICAL 🚨      | Alert detected      |
| QUERY ❓          | Question detected   |
| NORMAL ✅         | Default             |

---

## 🗂️ Project Structure

```
📁 SentimentAnalysisProject
│
├── 📄 sample.txt
├── 🐍 add_data.py
├── 🐍 view_data.py
├── 🗄️ sen.db
├── 📘 README.md
└── 🖼️ architecture.png
```

---

## 🗄️ Database Schema

### Database Name: `sen.db`

### Table Name: `results`

| Column         | Type    | Description                   |
| -------------- | ------- | ----------------------------- |
| id             | INTEGER | Primary Key                   |
| sentence       | TEXT    | Input sentence                |
| sentiment      | TEXT    | POSITIVE / NEGATIVE / NEUTRAL |
| score          | INTEGER | Sentiment score               |
| positive_count | INTEGER | Positive words count          |
| negative_count | INTEGER | Negative words count          |
| pattern        | TEXT    | Pattern type                  |
| tag            | TEXT    | Content classification        |

---

## ⚙️ How to Run

### Step 1️⃣ Place sample.txt

Example:

```
This is a good system.
This is a bad error.
The system is amazing.
Is the system working?
```

---

### Step 2️⃣ Run Analysis

```
python add_data.py
```

Output:

```
New database sen.db created
Processing 4 sentences
Analysis completed
```

---

### Step 3️⃣ View Results

```
python view_data.py
```

Output:

```
ID | Sentiment | Score | Pattern | Tag | Sentence
1  | POSITIVE  | 1     | NORMAL  | POSITIVE | This is a good system
2  | NEGATIVE  | -2    | ALERT   | CRITICAL | This is a bad error
```

---

## 🧵 Parallel Processing Used

| Component          | Purpose                      |
| ------------------ | ---------------------------- |
| ThreadPoolExecutor | Parallel sentence processing |
| Writer Thread      | Safe database writing        |
| Queue              | Thread communication         |

---

## 📊 Performance Benefits

| Feature               | Benefit             |
| --------------------- | ------------------- |
| Parallel Processing ⚡ | Faster execution    |
| Multithreading 🧵     | Efficient CPU usage |
| SQLite 🗄️            | Lightweight storage |
| Rule-based 🧠         | Simple and fast     |

---

## 💻 Technologies Used

| Technology    | Purpose              |
| ------------- | -------------------- |
| Python 🐍     | Programming language |
| SQLite 🗄️    | Database             |
| ThreadPool 🧵 | Parallel processing  |
| Regex 🔍      | Text processing      |

---

## 🎯 Applications

* 📱 Social media analysis
* 🛒 Product review analysis
* 🧾 Customer feedback analysis
* ⚠️ Log monitoring systems
* 🤖 AI preprocessing

---

## 🔮 Future Improvements

* 📊 Dashboard visualization
* 📁 CSV export
* 🌐 Web interface
* 🤖 Machine learning integration
* 📧 Email reporting

---

## 👨‍💻 Author

**LINGESH K**
🎓 BE Electrical and Electronics Engineering

---

## ✅ Conclusion

This project successfully demonstrates:

* 🧵 Parallel Processing
* 🧠 Sentiment Analysis
* 🗄️ Database Storage
* ⚡ High Performance Processing

It is a scalable and efficient text processing system.

---

⭐ *End of README*
