# 🚀 Space Launches API & Kubernetes Pipeline

## Overview
The **Space Launches Data API** is a containerized microservice suite that:

1. Fetches & normalizes the Kaggle “One Small Step for Data” Global Space Launches CSV, handling header quirks and imputing missing rocket counts.

2. **Caches** every launch record in Redis (db 0) for low-latency access.

3. Exposes a **Flask REST API** to load (/data), query (GET /data), and delete (DELETE /data) launch records.

4. Provides a suite of analysis endpoints—/analyze/timeline, /analyze/sector, /analyze/geography, and /analyze/top-private—which **enqueue jobs** for background processing.

5. Offers a **Jobs API** (/jobs/<job_id>) so clients can poll job status and a **Results API** (/results/<job_id>) to download the generated PNG plots.

6. Runs a **Worker** service that pulls tasks off a Redis list (db 1), updates job metadata (db 2), runs the appropriate plotting routine (timeline crossover, sector bar, geographic heatmap, top-private bar), and stores the raw PNG bytes in Redis (db 3).

## Project Files  
*(The following files and folders comprise this repository.  The `data/` and `results/` directories are not checked in—you’ll create or populate them locally.)*
- `Dockerfile`  
- `docker-compose.yml`  
- `diagram.png`  
- `kubernetes/`  
- `src/`  
- `test/`  
- `.gitignore`  
- `pytest.ini`  
- `requirements.txt`  
- `README.md`  

---

## Introduction  
We provide a containerized Flask+Redis API for ingesting, normalizing, and analyzing a global space-launches dataset.  Users can submit background jobs to generate timeline, sector, geography and “top-private provider” plots—then download the resulting PNGs.

---

## Data Preparation  
1. **Kaggle CSV**: “One Small Step for Data” Global Space Launches (https://www.kaggle.com/datasets/davidroberts13/one-small-step-for-data)  
2. **Kaggle API Token**:  
   - Copy your `kaggle.json` token into `~/.kaggle/kaggle.json` (inside your VM or Docker host).  
   - Lock down permissions:  
     ```bash
     chmod 600 ~/.kaggle/kaggle.json
     ```  
3. **Columns of Interest**:  
   - `Year`, `Private or State Run` (P/S), `Company Name`, `Country of Launch`, `# Rocket`  

---

## Architecture Diagram  
![Architecture Diagram](diagram.png)

---

## Key Technologies  
- **Docker & Docker Compose** for local container orchestration  
- **Flask** for REST API endpoints  
- **Redis** (db 0…3) for record storage, job queue, metadata, and result caching  
- **Pandas & Matplotlib** for data cleaning and static plotting  
- **(Kubernetes)** manifests (in `kubernetes/`) for future production rollout  

---

## Deployment (Local Hardware)  
1. Install Docker & Docker Compose.  
2. Ensure your Kaggle token is in `~/.kaggle/kaggle.json` with `chmod 600`.  
3. From repo root:  
   ```bash
   docker-compose up --build -d
