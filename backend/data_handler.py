import pandas as pd
import os
from pathlib import Path

DATA_DIRECTORY = Path("assets/data/")

"""
loads csv file, save as parquet
"""
def optimize_data(file_name: str):
    file_path = DATA_DIRECTORY / file_name
    base, ext = os.path.splitext(file_path)
    parquet_path = base + '.parquet'
    if os.path.exists(parquet_path):
        print(f"📄 Load from Parquet: {parquet_path}")
        df = pd.read_parquet(parquet_path)
    else:
        print(f"🛠️ Parquet not found. Load CSV: {file_path}")
        df = pd.read_csv(file_path)

        # Parquet abspeichern für spätere schnelle Ladezeiten
        print(f"💾 Speichere Parquet: {parquet_path}")
        df.to_parquet(parquet_path, compression='snappy')
    return df