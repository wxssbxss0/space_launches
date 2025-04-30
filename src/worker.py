import os
import redis
import json
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pandas as pd
from jobs import set_job_status

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=True)
DATA_KEY = "space_launches"

def plot_private_crossover(records):
    import io
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.DataFrame(records)

    # 0) Map the raw sector field into a clean 'Sector' column
    sector_map = {"P": "Private", "S": "State"}
    if "Private or State Run" not in df.columns:
        raise KeyError("Expected 'Private or State Run' in data")
    df['Sector'] = df['Private or State Run'].map(sector_map).fillna("Other")

    # 1) Ensure Year is integer
    df['Year'] = df['Year'].astype(int)

    # 2) Pivot counts by Year × Sector
    pivot = df.pivot_table(
        index='Year',
        columns='Sector',
        values='id',
        aggfunc='count',
        fill_value=0
    )

    # 3) Find the first Year where Private > State
    if 'Private' not in pivot.columns or 'State' not in pivot.columns:
        raise KeyError(f"Pivot missing expected columns, got {list(pivot.columns)}")
    crossover_mask = pivot['Private'] > pivot['State']
    first_cross = crossover_mask.idxmax() if crossover_mask.any() else None

    # 4) Plot both series
    fig, ax = plt.subplots(figsize=(8, 4))
    pivot['State'].plot(ax=ax, label='State')
    pivot['Private'].plot(ax=ax, label='Private')

    # 5) Annotate crossover if it exists
    if first_cross is not None:
        y = pivot.loc[first_cross, 'Private']
        ax.annotate(
            f'Crossover: {first_cross}',
            xy=(first_cross, y),
            xytext=(first_cross, y + max(pivot.max())*0.05),
            arrowprops=dict(arrowstyle='->', lw=1.5)
        )

    ax.set_title('State vs Private Launches Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Launches')
    ax.legend()
    plt.tight_layout()

    # 6) Serialize to PNG bytes
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf.read()

def plot_sector(df):
    sector_map = {"P": "Private", "S": "State"}
    df['Sector'] = df['Private or State Run'].map(sector_map)
    sector_counts = df['Sector'].value_counts()
    plt.figure(figsize=(6,4))
    sector_counts.plot(kind='bar', color=['#1f77b4','#ff7f0e'])
    plt.title("Launches by Sector")
    plt.xlabel("Sector")
    plt.ylabel("Number of Launches")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf.read()

def plot_geography(df):
    country_counts = df['Country of Launch'].value_counts()
    plt.figure(figsize=(10,6))
    sns.heatmap(country_counts.values.reshape(-1,1), annot=True, fmt="d", yticklabels=country_counts.index, cmap="YlOrRd", cbar=False)
    plt.title("Launches by Country (Heatmap)")
    plt.xlabel("Launch Count")
    plt.ylabel("Country")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf.read()

def process_job(job_id, job_type):
    all_data = r.hvals(DATA_KEY)
    if not all_data:
        set_job_status(job_id, "failed")
        return
    df = pd.DataFrame([json.loads(d) for d in all_data])
    if job_type == "timeline":
        img_bytes = plot_private_crossover(df)
    elif job_type == "sector":
        img_bytes = plot_sector(df)
    elif job_type == "geography":
        img_bytes = plot_geography(df)
    else:
        set_job_status(job_id, "failed")
        return
    r.hset("results", job_id, img_bytes)
    set_job_status(job_id, "complete")

def main():
    while True:
        job_id = r.brpoplpush("hot_queue", "processing_queue", timeout=0)
        job_data = r.hget("jobs", job_id)
        if job_data:
            job = json.loads(job_data)
            process_job(job_id, job["type"])
            r.lrem("processing_queue", 0, job_id)
        time.sleep(1)

if __name__ == "__main__":
    main()

