"""
app.py — Flask application entry point & route definitions
"""
import threading
import uuid
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

from flask import Flask, jsonify, render_template, request

from database import (
    clear_db, fetch_all, get_aggregate_stats,
    get_score_distribution, init_db, insert_chunk, insert_many
)
from processor import (
    analyze_chunk, split_into_paragraphs, split_into_sentences,
    extract_text_from_file
)

app = Flask(__name__)

# ── Global job state (one job at a time) ────────────────────────────────────
_job: Dict[str, Any] = {
    "running":    False,
    "total":      0,
    "done":       0,
    "batch_id":   "",
    "log":        [],       # list of log-line strings
    "error":      None,
    "start_time": None,
    "duration":   0,
}
_job_lock = threading.Lock()


def _log(msg: str):
    ts  = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with _job_lock:
        _job["log"].append(line)
        if len(_job["log"]) > 200:          # cap memory
            _job["log"] = _job["log"][-200:]


# ── Processing pipeline (runs in background thread) ─────────────────────────
def _run_pipeline(text: str, method: str, workers: int):
    with _job_lock:
        _job["running"]  = True
        _job["done"]     = 0
        _job["error"]    = None
        _job["log"]      = []
        batch_id = datetime.now().strftime("B_%Y%m%d_%H%M%S")
        _job["batch_id"] = batch_id

    chunks = split_into_sentences(text) if method == "sentence" else split_into_paragraphs(text)

    if not chunks:
        with _job_lock:
            _job["running"] = False
            _job["error"]   = "No valid chunks found."
        return

    with _job_lock:
        _job["total"] = len(chunks)
        _job["start_time"] = time.time()

    _log(f"Batch {batch_id} | {len(chunks)} chunks | {workers} threads | {method}")

    batch_buffer = []
    BATCH_SIZE = 100

    with ThreadPoolExecutor(max_workers=workers) as ex:
        fmap = {ex.submit(analyze_chunk, ch): ch for ch in chunks}
        for fut in as_completed(fmap):
            with _job_lock:
                if not _job["running"]:
                    break
            chunk = fmap[fut]
            try:
                r = fut.result()
                # Prepare data for batch insert
                ts = datetime.now().isoformat(timespec='seconds')
                row = (batch_id, chunk, r["score"], r["label"],
                       r["pos"], r["neg"], r["neu"], r["wc"], ts)
                batch_buffer.append(row)

                if len(batch_buffer) >= BATCH_SIZE:
                    insert_many(batch_buffer)
                    batch_buffer = []

                with _job_lock:
                    _job["done"] += 1
                    _job["duration"] = round(time.time() - _job["start_time"], 1)

                icon = "✅" if r["label"] == "Positive" else ("❌" if r["label"] == "Negative" else "➖")
                _log(f"{icon} [{r['label']:8s}] {chunk[:55].replace(chr(10),'⏎')}…")
            except Exception as e:
                _log(f"ERROR: {e}")

    # Final flush
    if batch_buffer:
        insert_many(batch_buffer)

    with _job_lock:
        _job["duration"] = round(time.time() - _job["start_time"], 1)
        _job["running"] = False

    _log(f"🎉 Done — {_job['done']} / {_job['total']} chunks processed in {_job['duration']}s.")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — Pages
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — API
# ══════════════════════════════════════════════════════════════════════════════

# ── Processing ───────────────────────────────────────────────────────────────
@app.route("/api/process", methods=["POST"])
def api_process():
    with _job_lock:
        if _job["running"]:
            return jsonify({"error": "A job is already running."}), 409

    data    = request.get_json(force=True)
    text    = (data.get("text") or "").strip()
    method  = data.get("method", "sentence").lower()
    workers = min(max(int(data.get("workers", 4)), 1), 16)

    if not text:
        return jsonify({"error": "No text supplied."}), 400

    t = threading.Thread(target=_run_pipeline, args=(text, method, workers), daemon=True)
    t.start()
    return jsonify({"status": "started"})


@app.route("/api/extract", methods=["POST"])
def api_extract():
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    combined_text = []
    
    for file in files:
        if file.filename:
            text = extract_text_from_file(file, file.filename)
            combined_text.append(text)
            
    return jsonify({"text": "\n\n".join(combined_text)})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    with _job_lock:
        _job["running"] = False
    return jsonify({"status": "stopped"})


@app.route("/api/progress")
def api_progress():
    with _job_lock:
        return jsonify({
            "running":  _job["running"],
            "total":    _job["total"],
            "done":     _job["done"],
            "batch_id": _job["batch_id"],
            "log":      _job["log"][-40:],   # last 40 lines
            "error":    _job["error"],
            "pct":      round(_job["done"] / _job["total"] * 100, 1) if _job["total"] else 0,
            "duration": _job["duration"],
        })


# ── Results ──────────────────────────────────────────────────────────────────
@app.route("/api/results")
def api_results():
    keyword  = request.args.get("keyword", "").strip()
    min_sc   = request.args.get("min_score", type=int)
    max_sc   = request.args.get("max_score", type=int)
    label    = request.args.get("label", "All")
    limit    = request.args.get("limit", default=500, type=int)
    offset   = request.args.get("offset", default=0, type=int)
    
    rows     = fetch_all(keyword, min_sc, max_sc, label, limit, offset)
    stats    = get_aggregate_stats()
    scores   = get_score_distribution()
    return jsonify({"rows": rows, "stats": stats, "scores": scores})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    clear_db()
    return jsonify({"status": "cleared"})


# ── Export ───────────────────────────────────────────────────────────────────
@app.route("/api/export")
def api_export():
    import csv, io
    label = request.args.get("label", "All")
    rows  = fetch_all(sentiment_filter=label)
    if not rows:
        return jsonify({"error": "No data"}), 404

    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    output = buf.getvalue()

    from flask import Response
    fname = f"text_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
