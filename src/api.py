import os
import uuid
import json
import io
from flask import Flask, request, jsonify, send_file
import redis
import pandas as pd
from jobs import create_job, get_job, job_result_ready

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=True)
DATA_KEY = "space_launches"

@app.route("/help", methods=["GET"])
def help():
    return jsonify({
        "/help": "GET - List all endpoints and their usage.",
        "/data": "GET - List all records. POST - Upload new records (CSV or JSON). DELETE - Delete all records.",
        "/analyze/timeline": "POST - Submit a timeline analysis job (returns launches per year plot).",
        "/analyze/sector": "POST - Submit a sector comparison job (returns bar chart).",
        "/analyze/geography": "POST - Submit a geographical analysis job (returns heatmap).",
        "/jobs/<job_id>": "GET - Get job status and result.",
        "/results/<job_id>": "GET - Download generated plot/image."
    })

@app.route("/data", methods=["GET", "POST", "DELETE"])
def data_collection():
    if request.method == "GET":
        keys = r.hkeys(DATA_KEY)
        data = r.hmget(DATA_KEY, keys)
        return jsonify([json.loads(d) for d in data if d])
    elif request.method == "POST":
        # Accept CSV upload or JSON
        if request.content_type.startswith("multipart/form-data"):
            file = request.files.get("file")
            if not file or not file.filename.endswith(".csv"):
                return jsonify({"error": "CSV file required"}), 400
            df = pd.read_csv(file)
            records = df.to_dict(orient="records")
        else:
            records = request.get_json()
            if not isinstance(records, list):
                records = [records]
        for record in records:
            record_id = str(uuid.uuid4())
            record["id"] = record_id
            r.hset(DATA_KEY, record_id, json.dumps(record))
        return jsonify({"status": "success", "count": len(records)}), 201
    elif request.method == "DELETE":
        r.delete(DATA_KEY)
        return jsonify({"status": "all records deleted"})

def submit_analysis_job(job_type):
    job_id = create_job(job_type)
    return jsonify({"job_id": job_id}), 202

@app.route("/analyze/timeline", methods=["POST"])
def analyze_timeline():
    return submit_analysis_job("timeline")

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

