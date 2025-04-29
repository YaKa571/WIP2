import os
from pathlib import Path

import pandas as pd

DATA_DIRECTORY = Path("assets/data/")


def optimize_data(*file_names: str):
    """
    Optimize data processing by converting a CSV file to a Parquet file for better performance and storage
    efficiency. If a corresponding Parquet file already exists, it will be used directly instead of
    reloading and converting the CSV file.

    Args:
        file_name (str): Name of the input CSV file to be processed.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    for file_name in file_names:
        file_path = DATA_DIRECTORY / file_name
        base, ext = os.path.splitext(file_path)
        parquet_path = base + '.parquet'
        if os.path.exists(parquet_path):
            print(f"ℹ️ Loading from Parquet: {parquet_path}")
        else:
            print(f"⚠️ Parquet not found. Loading and converting CSV: {file_path}")
            df = pd.read_csv(file_path)

            print(f"ℹ️ Saved Parquet: {parquet_path}")
            df.to_parquet(parquet_path, compression='snappy')
