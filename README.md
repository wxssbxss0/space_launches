# 🚀 Space Launches API & Kubernetes Pipeline

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
