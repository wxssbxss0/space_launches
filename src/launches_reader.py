# launches_reader.py

import os
import tempfile
import pandas as pd
from typing import List, Dict
from kaggle.api.kaggle_api_extended import KaggleApi

# Cache so we only download once per process
_cached_launches_data: List[Dict] = None

def read_launches_data(filepath: str = None) -> List[Dict]:
    """
    Reads Global Space Launches data either from:
      • a local CSV file (if filepath is provided), or
      • the Kaggle dataset (if filepath is None).
    It then:
      1) strips whitespace from headers,
      2) finds the rocket-count column dynamically,
      3) coerces to numeric and imputes missing values with a safe median,
      4) caches the remote result,
      5) returns a list of JSON-serializable dicts.
    """
    global _cached_launches_data

    # 0) Return cache if we've already fetched remotely
    if filepath is None and _cached_launches_data is not None:
        return _cached_launches_data

    # 1) Load DataFrame
    if filepath:
        df = pd.read_csv(filepath)
    else:
        api = KaggleApi()
        api.authenticate()

        with tempfile.TemporaryDirectory() as tmpdir:
            api.dataset_download_files(
                'davidroberts13/one-small-step-for-data',
                path=tmpdir, unzip=True, force=True
            )
            # find any CSV in that temp dir
            csv_files = [f for f in os.listdir(tmpdir) if f.lower().endswith('.csv')]
            if not csv_files:
                raise FileNotFoundError(f"No CSV found in {tmpdir}")
            csv_path = os.path.join(tmpdir, csv_files[0])
            df = pd.read_csv(csv_path)

    # 2) Normalize headers
    df.columns = df.columns.str.strip()

    # 3) Locate the rocket-count column
    rocket_cols = [c for c in df.columns if 'rocket' in c.lower()]
    if not rocket_cols:
        raise KeyError(f"No column containing 'rocket' found; got {df.columns.tolist()}")
    rocket_col = rocket_cols[0]

    # 4) Safe numeric conversion & imputation
    series = pd.to_numeric(df[rocket_col], errors='coerce')
    valid = series.dropna()
    if not valid.empty:
        med_value = valid.median()
    else:
        med_value = 0  # default if no valid numbers
    median = int(med_value)
    df[rocket_col] = series.fillna(median).astype(int)

    # 5) Convert to list of dicts
    records = df.to_dict(orient='records')

    # 6) Cache remote fetch
    if filepath is None:
        _cached_launches_data = records

    return records

