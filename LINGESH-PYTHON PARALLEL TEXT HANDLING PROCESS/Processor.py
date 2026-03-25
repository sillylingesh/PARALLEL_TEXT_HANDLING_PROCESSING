"""
processor.py — Text chunking & rule-based sentiment analysis engine
"""
import re

# ── Sentiment word lists ────────────────────────────────────────────────────
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic",
    "happy", "joy", "love", "best", "perfect", "positive", "brilliant",
    "outstanding", "superb", "awesome", "nice", "beautiful", "enjoy",
    "success", "win", "gain", "improve", "effective", "efficient",
    "helpful", "useful", "clear", "strong", "safe", "bright", "hope",
    "pleased", "thankful", "grateful", "innovative", "exciting", "proud",
    "impressive", "delightful", "creative", "inspiring", "motivated",
    "confident", "optimistic", "cheerful", "enthusiastic", "reliable",
    "trustworthy", "productive", "rewarding", "fascinating", "valuable"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "sad", "angry", "hate",
    "worst", "poor", "negative", "fail", "error", "problem", "issue",
    "wrong", "difficult", "hard", "slow", "weak", "dangerous", "dark",
    "lose", "loss", "broken", "damage", "risk", "threat", "fear",
    "worry", "concern", "painful", "unfortunate", "regret", "disappointed",
    "frustrated", "useless", "inefficient", "confusing", "complex", "boring",
    "harmful", "severe", "critical", "unstable", "unreliable", "failing",
    "corrupt", "flawed", "defective", "inadequate", "miserable", "hopeless"
}


# ── Chunking strategies ─────────────────────────────────────────────────────
def split_into_sentences(text: str) -> list[str]:
    """Split at sentence boundaries (. ! ?)."""
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw if len(s.strip()) > 1]


def split_into_paragraphs(text: str) -> list[str]:
    """Split on blank lines."""
    return [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]


# ── Sentiment analysis ──────────────────────────────────────────────────────
def analyze_chunk(chunk: str) -> dict:
    """Pure rule-based sentiment — thread-safe, no I/O."""
    words     = re.findall(r'\b[a-zA-Z]+\b', chunk.lower())
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    neu_count = len(words) - pos_count - neg_count
    score     = pos_count - neg_count

    if   score > 0: label = "Positive"
    elif score < 0: label = "Negative"
    else:           label = "Neutral"

    return {
        "score": score, "label": label,
        "pos": pos_count, "neg": neg_count,
        "neu": neu_count, "wc": len(words)
    }