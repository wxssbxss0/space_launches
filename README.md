# COE 332 Final Project: Space Launches API 🚀 & Kubernetes Pipeline

## Overview
The **Space Launches Data API** is a containerized microservice suite that:

1. **Fetches & normalizes** the Kaggle “One Small Step for Data” Global Space Launches CSV, handling header quirks and imputing missing rocket counts.

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
- `pytest.ini`  
- `requirements.txt`  
- `README.md`  

---

## Introduction  
We provide a containerized Flask+Redis API for ingesting, normalizing, and analyzing a global space-launches dataset.  Users can submit background jobs to generate **timeline**, **sector**, **geography** and **top-private provider** plots— then download the resulting PNGs.

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
   docker compose up --build 

## Project Overview

This project performs the following operations:

1. **Space Launch Data Handling:**  
   - Downloads (via Kaggle API) or reads a local CSV of global space launches.  
   - Normalizes headers (strips whitespace), imputes missing `# Rocket` values, and resolves “Sea Launch” entries.  
   - Caches every launch record in Redis (db 0) for fast retrieval.  
   - Exposes endpoints to load (`POST /data`), list (`GET /data`), and delete (`DELETE /data`) launch records.

2. **Jobs API:**  
   - Provides analysis endpoints that enqueue background jobs for plotting:  
     - `/analyze/timeline` (crossover analysis)  
     - `/analyze/sector` (private vs. state bar chart)  
     - `/analyze/geography` (country heatmap)  
     - `/analyze/top-private` (top-10 private providers)  
   - Each job is assigned a UUID and stored in Redis (db 1 as a list, db 2 for metadata).  
   - Clients poll `/jobs/<job_id>` to check status and `/results/<job_id>` to download the resulting PNG.

3. **Worker Integration:**  
   A dedicated worker process continuously:  
   - BLPOPs a job ID from Redis db 1, marks it “in progress” in db 2.  
   - Loads the full launch cache from Redis db 0.  
   - Runs the appropriate plotting function (`plot_private_crossover`, `plot_sector`, `plot_geography`, or `plot_top_private`).  
   - Stores the raw PNG bytes under `results:<job_id>` in Redis db 3 and marks the job “complete” in db 2.


| Route                      | Method | Description                                                                              |
| -------------------------- | :----: | ---------------------------------------------------------------------------------------- |
| **`/help`**                |   GET  | List all endpoints and usage.                                                            |
| **`/data`**                |   GET  | Get all records (seeds from Kaggle CSV if empty).                                        |
|                            |  POST  | Upload CSV (`file`) or JSON array/object to seed/append records.                         |
|                            | DELETE | Delete all records.                                                                      |
| **`/analyze/timeline`**    |  POST  | Enqueue crossover analysis: marks the first year private launches exceed state launches. |
| **`/analyze/sector`**      |  POST  | Enqueue sector comparison: bar chart of private vs. state launches.                      |
| **`/analyze/geography`**   |  POST  | Enqueue geographic analysis: heatmap of launches by country.                             |
| **`/analyze/top-private`** |  POST  | Enqueue top-private job: top 10 private launch providers (1995–2020).                    |
| **`/jobs/<job_id>`**       |   GET  | Query job status & metadata (`queued`/`complete`, type, `result_ready` flag).            |
| **`/results/<job_id>`**    |   GET  | Download the PNG bytes for a completed job.                                              |

