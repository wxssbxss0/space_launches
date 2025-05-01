import os
import uuid
import json
import io
from flask import Flask, request, jsonify, send_file
import redis
import pandas as pd
from jobs import create_job, get_job, job_result_ready
from launches_reader import read_launches_data


app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=False)
DATA_KEY = "space_launches"

@app.route("/help", methods=["GET"])
def help():
    return jsonify({
        "/help": "GET - List all endpoints and their usage.",
        "/data": "GET - List all records. POST - Upload new records (CSV or JSON). DELETE - Delete all records.",
        "/analyze/timeline": "POST - Submit a crossover analysis job (identifies the first year when private launches exceeded state launches).",
        "/analyze/sector": "POST - Submit a sector comparison job (returns a bar chart of private vs. state launches).",
        "/analyze/geography": "POST - Submit a geographical analysis job (returns a world‐map view of launch counts by country).",
        "/analyze/top-private": "POST - Submit a top‐private analysis job (returns a bar chart of the top 10 private launch providers from 1995–2020).",
        "/jobs/<job_id>": "GET - Get job status and metadata for the given job ID.",
        "/results/<job_id>": "GET - Download the generated plot/image for a completed job."
    })

@app.route("/data", methods=["GET", "POST", "DELETE"])
def data_collection():
    # ──────── GET ────────
    if request.method == "GET":
        # 1) grab all values
        raw = r.hvals(DATA_KEY)

        # 2) if empty, seed from Kaggle CSV
        if not raw:
            launches = read_launches_data()  # pulls via Kaggle API
            for rec in launches:
                rec_id = str(uuid.uuid4())
                rec["id"] = rec_id
                r.hset(DATA_KEY, rec_id, json.dumps(rec))
            raw = r.hvals(DATA_KEY)

        # 3) return JSON
        return jsonify([json.loads(d) for d in raw])

    # ──────── POST ────────
    elif request.method == "POST":
        # a) file‐upload?
        if request.files.get("file"):
            file = request.files["file"]
            if not file.filename.lower().endswith(".csv"):
                return jsonify({"error": "CSV file required"}), 400
            records = read_launches_data(file)

        else:
            # b) JSON payload?
            payload = request.get_json(force=True, silent=True)

            if isinstance(payload, dict) and "url" in payload:
                # ignore payload["url"] – read_launches_data() already knows Kaggle
                records = read_launches_data()

            elif payload:
                # wrap single obj in list
                records = payload if isinstance(payload, list) else [payload]

            else:
                # c) bare POST → seed full dataset
                records = read_launches_data()

        # stash into Redis
        for rec in records:
            rec_id = str(uuid.uuid4())
            rec["id"] = rec_id
            r.hset(DATA_KEY, rec_id, json.dumps(rec))

        return jsonify({"status": "success", "count": len(records)}), 201

    # ──────── DELETE ────────
    elif request.method == "DELETE":
        r.delete(DATA_KEY)
        return jsonify({"status": "all records deleted"}), 200


def submit_analysis_job(job_type):
    job_id = create_job(job_type)
    return jsonify({"job_id": job_id}), 202

@app.route("/analyze/timeline", methods=["POST"])
def analyze_timeline():
    return submit_analysis_job("timeline")

@app.route("/analyze/top-private", methods=["POST"])
def analyze_top_private():
    return submit_analysis_job("top_private")

@app.route("/analyze/sector", methods=["POST"])
def analyze_sector():
    return submit_analysis_job("sector")

@app.route("/analyze/geography", methods=["POST"])
def analyze_geography():
    return submit_analysis_job("geography")

@app.route("/jobs/<job_id>", methods=["GET"])
def job_status(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    job["result_ready"] = job_result_ready(job_id)
    return jsonify(job)

@app.route("/results/<job_id>", methods=["GET"])
def get_result(job_id):
    img_bytes = r.hget("results", job_id)
    if not img_bytes:
        return jsonify({"error": "Result not found"}), 404
    return send_file(io.BytesIO(img_bytes), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

