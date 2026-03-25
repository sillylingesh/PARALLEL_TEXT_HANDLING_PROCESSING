# 🚀 Parallel Text Handling & Sentiment Analysis System

### 🧠 Python + SQLite + Parallel Processing

---

# 📌 Project Description

The **Parallel Text Handling Processing System** is a Python application that reads text data, analyzes the sentiment of each sentence, and stores the results in a **SQLite database**.

The system compares **Sequential Processing and Parallel Processing** to demonstrate how parallel execution improves performance when analyzing large text datasets.

This project demonstrates:

- ⚡ Parallel Processing  
- 🧵 Multithreading / Multiprocessing  
- 🗄️ SQLite Database Integration  
- 🧠 Rule-Based Sentiment Analysis  
- 📊 Structured Data Storage  
- ⏱️ Performance Comparison  

---

# 🖼️ System Architecture

```
           sample.txt
               │
               ▼
        Sentence Reader
               │
               ▼
        Sentence Splitter
               │
               ▼
      Parallel Processing Engine
   ┌─────────┬─────────┬─────────┐
   ▼         ▼         ▼         ▼
Sentence   Sentence   Sentence   Sentence
Analyzer   Analyzer   Analyzer   Analyzer
   │         │         │         │
   └─────────┴─────────┴─────────┘
               │
               ▼
        Database Writer
               │
               ▼
             sen.db
               │
               ▼
            view.py
```

---

# ✨ Features

## ⚙️ Core Features

- 📄 Automatic text file reading  
- ✂️ Sentence splitting  
- 😊 Positive sentiment detection  
- 😡 Negative sentiment detection  
- ⚖️ Sentiment score calculation  
- 🔍 Text pattern detection  
- 🏷️ Sentence tagging  
- 🧵 Parallel sentence processing  
- ⚡ Faster execution using multiprocessing  
- 🗄️ SQLite database storage  
- 👁️ Database result viewer  

---

# 🧠 Sentiment Logic

|          Condition              |   Result    |
|                              ---|          ---|
| Positive words > Negative words | 😊 POSITIVE |
| Negative words > Positive words | 😡 NEGATIVE |
| Equal words                     | 😐 NEUTRAL  |

---

# 🔍 Pattern Detection

| Pattern      | Detection |
|---           |        ---|
| QUESTION ❓ | Sentence contains `?` |
| ALERT ⚠️    | Contains words like error, failure, danger |
| LONG 📏     | Sentence length greater than 12 words |
| NORMAL ✅   | Default condition |

---

# 🏷️ Tagging System

| Tag              | Meaning |
|---               |---      |
| VERY_POSITIVE 🌟 | High positive score    |
| VERY_NEGATIVE 🔥 | High negative score    |
| CRITICAL 🚨      | Alert pattern detected |
| QUERY ❓         | Question detected      |
| NORMAL ✅        | Default classification |

---

# 🗂️ Project Structure

```
📁 PARALLEL_TEXT_HANDLING_PROCESSING
│
├── 📄 sample.txt
├── 🐍 Parallel_process.py
├── 🐍 Sequential_process.py
├── 🐍 app.py
├── 🐍 view.py
├── 🗄️ sen.db
├── 📘 README.md
```

---

# 🗄️ Database Schema

Database Name: **sen.db**

Table Name: **results**

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary Key |
| sentence | TEXT | Input sentence |
| sentiment | TEXT | POSITIVE / NEGATIVE / NEUTRAL |
| score | INTEGER | Sentiment score |
| positive_count | INTEGER | Positive word count |
| negative_count | INTEGER | Negative word count |
| pattern | TEXT | Sentence pattern |
| tag | TEXT | Content classification |

---

# ⚙️ How to Run

## Step 1️⃣ Clone the Repository

```bash
git clone https://github.com/sillylingesh/PARALLEL_TEXT_HANDLING_PROCESSING.git
```

## Step 2️⃣ Navigate to Project Folder

```bash
cd PARALLEL_TEXT_HANDLING_PROCESSING
```

## Step 3️⃣ Run Sequential Processing

```bash
python Sequential_process.py
```

Example Output

```
Processing sentences sequentially...
Execution Time : 3.21 seconds
```

## Step 4️⃣ Run Parallel Processing

```bash
python Parallel_process.py
```

Example Output

```
Processing sentences using parallel processing...
Execution Time : 0.702 seconds
```

## Step 5️⃣ View Stored Results

```bash
python view.py
```

Example Output

```
ID | Sentiment | Score | Pattern | Tag           | Sentence
1  | POSITIVE  | 2     | NORMAL  | VERY_POSITIVE | This system is amazing
2  | NEGATIVE  | -2    | ALERT   | CRITICAL      | This is a bad error
```

---

# 🧵 Parallel Processing Used

| Component | Purpose |
|---        |---      |
| Multiprocessing  | Parallel sentence analysis |
| Worker Processes | Execute sentiment analysis |
| SQLite Database  | Store processed results |

---

# 📊 Performance Benefits

| Feature | Benefit |
|---      |      ---|
| Parallel Processing ⚡ | Faster execution |
| Multiprocessing 🧵     | Utilizes multiple CPU cores |
| SQLite 🗄️              | Lightweight database |
| Rule-based NLP 🧠      | Simple and fast sentiment detection |

---

# 💻 Technologies Used

| Technology | Purpose |
|---         |---|
| Python 🐍 | Programming language |
| SQLite 🗄️ | Database |
| Multiprocessing ⚡ | Parallel processing |
| Regex 🔍 | Text cleaning and pattern detection |

---

# 🎯 Applications

- 📱 Social media sentiment analysis  
- 🛒 Product review analysis  
- 🧾 Customer feedback analysis  
- ⚠️ Log monitoring systems  
- 🤖 AI data preprocessing  

---

# 🔮 Future Improvements

- 📊 Data visualization dashboard  
- 📁 CSV / Excel export  
- 🌐 Web interface using Flask  
- 🤖 Machine learning sentiment analysis  
- 📈 Performance optimization  

---

# 👨‍💻 Author

**LINGESH K**

🎓 BE Electrical and Electronics Engineering  
🏫 RMK Engineering College  
 
---

# ✅ Conclusion

This project successfully demonstrates:

- 🧵 Parallel Processing  
- 🧠 Rule-Based Sentiment Analysis  
- 🗄️ Database Storage  
- ⚡ Efficient Text Processing  

It is a **scalable and efficient system for processing large text datasets using Python.**

---

⭐ End of README