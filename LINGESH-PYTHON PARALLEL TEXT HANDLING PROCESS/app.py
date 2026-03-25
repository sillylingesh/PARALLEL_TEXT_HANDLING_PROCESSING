"""
app.py — Flask application entry point & route definitions
"""
import threading
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, render_template, request

from database import (
    clear_db, fetch_all, get_aggregate_stats,
    get_score_distribution, init_db, insert_chunk,
)
from processor import analyze_chunk, split_into_paragraphs, split_into_sentences

app = Flask(__name__)

# ── Global job state (one job at a time) ────────────────────────────────────
_job = {
    "running":   False,
    "total":     0,
    "done":      0,
    "batch_id":  "",
    "log":       [],       # list of log-line strings
    "error":     None,
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

    _log(f"Batch {batch_id} | {len(chunks)} chunks | {workers} threads | {method}")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        fmap = {ex.submit(analyze_chunk, ch): ch for ch in chunks}
        for fut in as_completed(fmap):
            with _job_lock:
                if not _job["running"]:
                    break
            chunk = fmap[fut]
            try:
                r = fut.result()
                insert_chunk(batch_id, chunk, r["score"], r["label"],
                             r["pos"], r["neg"], r["neu"], r["wc"])
                with _job_lock:
                    _job["done"] += 1
                icon = "✅" if r["label"] == "Positive" else ("❌" if r["label"] == "Negative" else "➖")
                _log(f"{icon} [{r['label']:8s}] {chunk[:55].replace(chr(10),'⏎')}…")
            except Exception as e:
                _log(f"ERROR: {e}")

    with _job_lock:
        _job["running"] = False

    _log(f"🎉 Done — {_job['done']} / {_job['total']} chunks processed.")


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
        })


# ── Results ──────────────────────────────────────────────────────────────────
@app.route("/api/results")
def api_results():
    keyword  = request.args.get("keyword", "").strip()
    min_sc   = request.args.get("min_score", type=int)
    max_sc   = request.args.get("max_score", type=int)
    label    = request.args.get("label", "All")
    rows     = fetch_all(keyword, min_sc, max_sc, label)
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
    app.run(debug=True, port=5000)