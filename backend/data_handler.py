import json
from typing import Any

import pandas as pd
import pyarrow as pa
from pandas import DataFrame
from pyarrow.parquet import ParquetFile

import utils.logger as logger
from components.constants import DATA_DIRECTORY
from utils.benchmark import Benchmark


merchant_other_threshold = 1000 #default value, will be modified in read_parquet_data()


def read_parquet_data(file_name: str, num_rows: int = None, sort_alphabetically: bool = False) -> pd.DataFrame:
    """
    Reads data from a Parquet file and returns it as a Pandas DataFrame. This function provides options for reading
    a specific number of rows and sorting column names alphabetically. Additionally, if a file named
    'transactions_data.parquet' is being read and the number of rows is specified, a global threshold for grouping
    minor merchant groups is dynamically calculated.

    Args:
        file_name (str): Name of the Parquet file to be read. The file should exist in the pre-defined data directory.
        num_rows (int, optional): Number of rows to read from the Parquet file. If not specified or if the value is
            greater than or equal to the total number of rows, the entire file is read.
        sort_alphabetically (bool, optional): If True, the DataFrame's columns are sorted alphabetically. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame object containing the contents of the Parquet file.

    Raises:
        FileNotFoundError: If the specified Parquet file does not exist in the data directory.
    """
    file_path = DATA_DIRECTORY / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"⚠️ Parquet file not found: {file_path}")

    pf = ParquetFile(file_path)
    total_rows = pf.metadata.num_rows

    if num_rows is None or num_rows >= total_rows:
        df = pd.read_parquet(file_path, engine="pyarrow")
    else:
        batch = next(pf.iter_batches(batch_size=num_rows))
        df = pa.Table.from_batches(batches=[batch]).to_pandas()

    if sort_alphabetically:
        df = df.reindex(sorted(df.columns), axis=1)

    # dynamic threshold for grouping minor merchant groups
    if file_name == "transactions_data.parquet" and num_rows is not None:
        global merchant_other_threshold
        merchant_other_threshold = num_rows/50 #based on testing with 50_000 rows and threshold = 1000

    return df


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
            logger.log(f"ℹ️ Loading from Parquet: {parquet_path}", 2)
        else:
            logger.log(f"🔄 Converting CSV to Parquet: {csv_path}", 2)
            bm = Benchmark("Conversion")

            # Read CSV into DataFrame
            df = pd.read_csv(csv_path)
            # Write Parquet with fast encoding
            df.to_parquet(
                parquet_path,
                engine='pyarrow',
                compression='snappy',
            )
            logger.log(f"✅ Saved Parquet: {parquet_path}", 3)
            bm.print_time(level=3)


def clean_units(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans monetary unit symbols from the columns of a DataFrame.

    This function processes the columns of the input DataFrame and removes dollar
    signs from cell values, converting them into numeric values where applicable.
    Only columns where all non-empty cells start with a dollar sign are cleaned.
    Any column not matching these criteria remains unchanged. Cells are coerced
    to numeric types during processing.

    Args:
        df (pd.DataFrame): Input DataFrame to be cleaned.

    Returns:
        pd.DataFrame: A new DataFrame with monetary symbols removed and converted
        to numeric values where applicable.
    """
    new_df = df.copy()

    for col in df.columns:
        sample_values = df[col].dropna().astype(str)

        if sample_values.empty:
            continue

        # Check: does each cell start with "$"?
        if sample_values.str.startswith("$").all():
            # Remove $
            new_df[col] = sample_values.str[1:]  # Only cut off the first character
            new_df[col] = pd.to_numeric(new_df[col], errors="coerce")  # Convert to float

    return new_df


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

    logger.log(f"🔄 Converting JSON to DataFrame: {json_path}", 2)
    bm = Benchmark("Conversion")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    bm.print_time(level=3)

    return df


def json_to_dict(file_name: str) -> Any:
    """
    Converts a JSON file into a Python dictionary.

    This function reads a JSON file from the specified path and converts its
    contents into a Python dictionary. If the file does not exist, a
    FileNotFoundError is raised.

    Parameters:
        file_name (str): The name of the JSON file to be read, located in the
            DATA_DIRECTORY.

    Returns:
        Any: The data parsed from the JSON file as a Python object.

    Raises:
        FileNotFoundError: If the specified JSON file is not found.
    """
    json_path = DATA_DIRECTORY / file_name
    if not json_path.exists():
        raise FileNotFoundError(f"⚠️ JSON file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def get_mcc_description_by_merchant_id(mcc_dict: dict[str, str], merchant_id: int | str) -> str:
    """
    Fetch the Merchant Category Code (MCC) associated with a given merchant ID from a dictionary.
    If the merchant ID is invalid or not found in the dictionary, returns "Undefined".

    Args:
        mcc_dict (dict): A dictionary where merchant IDs (as strings) are mapped to their corresponding MCC.
        merchant_id (int | str): The merchant ID to lookup in the dictionary.

    Returns:
        str: The MCC associated with the given merchant ID, or "Undefined" if the ID is invalid or not found.
    """
    # Normalize string-key: Int->Str
    try:
        key = str(int(merchant_id))
    except (ValueError, TypeError):
        return "Undefined"

    # Lookup in Dictionary
    return mcc_dict.get(key, "Undefined")


def convert_transaction_columns_to_int(dataframe: DataFrame, columns: list[str]):
    """
    Convert specified transaction columns in the DataFrame to integer, when necessary.

    This function iterates through a list of specified columns in the provided
    DataFrame. For each column, it checks if the column's data type is integer.
    If not, it attempts to convert the column's data into integer values using
    `pandas.to_numeric`. The converted DataFrame is then saved to a predefined parquet
    file if any column has undergone conversion. For columns already in integer
    format, the function skips the conversion step for efficiency.

    Parameters:
    dataframe: DataFrame
        The input pandas DataFrame containing transaction data that may need
        type conversion for specified columns.

    columns: list[str]
        A list of column names within the DataFrame that are checked for integer
        type conversion.

    Returns:
    None
    """
    bm = Benchmark("Conversion")
    df = dataframe.copy()
    changed = False

    for col in columns:
        if not pd.api.types.is_integer_dtype(df[col]):
            logger.log(f"🔄 Converting '{col}' to integer...", 2)
            df[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(0)
                .astype(int)
            )
            changed = True
        else:
            logger.log(f"ℹ️ '{col}' is already integer, skipping.", 2)

    if changed:
        # Write once after all conversions
        df.to_parquet(
            DATA_DIRECTORY / "transactions_data.parquet",
            engine="pyarrow",
            compression="snappy",
            index=False
        )
        dataframe = df
        logger.log("✅ Converted columns to integer and updated parquet file", 2)
        bm.print_time(level=2)
    else:
        logger.log("ℹ️ No columns needed conversion, skipping parquet write", 2)
