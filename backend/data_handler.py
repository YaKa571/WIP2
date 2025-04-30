import json
from pathlib import Path

import pandas as pd

DATA_DIRECTORY = Path("assets/data/")


def optimize_data(*file_names: str):
    """
    Optimize data processing by converting a CSV file to a Parquet file for better performance and storage
    efficiency. If a corresponding Parquet file already exists, it will be used directly instead of
    reloading and converting the CSV file.

    Args:
        file_names (str): Name of the input CSV file to be processed.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    for file_name in file_names:
        csv_path = DATA_DIRECTORY / file_name
        if not csv_path.exists():
            raise FileNotFoundError(f"⚠️ CSV file not found: {csv_path}")

        parquet_path = csv_path.with_suffix('.parquet')
        csv_mtime = csv_path.stat().st_mtime

        # Only convert if Parquet missing or outdated
        if parquet_path.exists() and parquet_path.stat().st_mtime >= csv_mtime:
            print(f"ℹ️ Loading from Parquet: {parquet_path}")
        else:
            print(f"🔄 Converting CSV to Parquet: {csv_path}")
            # Read CSV into DataFrame
            df = pd.read_csv(csv_path)
            # Write Parquet with fast encoding
            df.to_parquet(
                parquet_path,
                engine='pyarrow',
                compression='snappy',
            )
            print(f"✅ Saved Parquet: {parquet_path}")


def clean_units(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Cleans currency or unit information from the input DataFrame `df` by handling
    columns where every value starts with a specific unit character (e.g., "$").
    Removes unit prefixes, converts the numeric part to a float, and returns a
    cleaned DataFrame along with a dictionary mapping units to their columns.

    :param df: The input DataFrame to be processed.
    :type df: pd.DataFrame
    :return: A tuple containing a modified DataFrame where currency or unit
        prefixes are removed and a dictionary mapping units to the columns
        in which they are found.
    :rtype: tuple[pd.DataFrame, dict]
    """
    unit_to_columns = {}
    new_df = df.copy()

    for col in df.columns:
        sample_values = df[col].dropna().astype(str)

        if sample_values.empty:
            continue

        # Check: does each cell start with "$"?
        if sample_values.str.startswith("$").all():
            unit = "$"
            unit_to_columns.setdefault(unit, set()).add(col)

            # Remove $
            new_df[col] = sample_values.str[1:]  # Only cut off the first character
            new_df[col] = pd.to_numeric(new_df[col], errors="coerce")  # Convert to float

    return new_df, unit_to_columns


def json_to_data_frame(file_name: str) -> pd.DataFrame:
    """
    Converts a JSON file into a Pandas DataFrame.

    The function reads a JSON file from the specified data directory,
    loads its content, and converts it into a Pandas DataFrame using the `pd.json_normalize` method.
    This is particularly useful for working with nested JSON structures and transforming them into
    a tabular format.

    Parameters:
    file_name: str
        The name of the JSON file to be converted into a DataFrame.

    Returns:
    pd.DataFrame
        A Pandas DataFrame representation of the loaded JSON data.

    Raises:
    FileNotFoundError
        If the JSON file does not exist at the specified path.
    """
    json_path = DATA_DIRECTORY / file_name
    if not json_path.exists():
        raise FileNotFoundError(f"⚠️ JSON file not found: {json_path}")

    print(f"ℹ️ Converting JSON to DataFrame: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return pd.json_normalize(data)
