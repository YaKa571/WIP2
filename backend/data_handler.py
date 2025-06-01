import json
from typing import Any

import pandas as pd
import pyarrow as pa
from pandas import DataFrame
from pyarrow.parquet import ParquetFile

import utils.logger as logger
from components.constants import DATA_DIRECTORY
from utils.benchmark import Benchmark


def read_parquet_data(file_name: str, num_rows: int = None, sort_alphabetically: bool = False) -> pd.DataFrame:
    """
    Reads a Parquet file into a pandas DataFrame.

    This function loads data from a specified Parquet file, with options to limit the
    number of rows and to sort column names alphabetically.

    Parameters:
    file_name: str
        The name of the Parquet file to read. Must exist in the DATA_DIRECTORY.
    num_rows: int, optional
        The number of rows to load from the Parquet file. By default, all rows
        are loaded. If specified, only the first num_rows will be loaded.
    sort_alphabetically: bool, optional
        If True, sort the column names alphabetically. Default is False.

    Returns:
    pd.DataFrame
        The pandas DataFrame containing the data from the Parquet file.

    Raises:
    FileNotFoundError
        If the specified file does not exist in the DATA_DIRECTORY.
    """
    file_path = DATA_DIRECTORY / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"⚠️ Parquet file not found: {file_path}")

    # Use optimized reading approach
    if num_rows is None:
        # Read all rows with optimized settings
        df = pd.read_parquet(
            file_path,
            engine="pyarrow",
            use_threads=True,  # Enable multi-threading
            memory_map=True  # Use memory mapping for better performance
        )
    else:
        # Read only the specified number of rows
        pf = ParquetFile(file_path)
        total_rows = pf.metadata.num_rows

        if num_rows >= total_rows:
            # If requesting more rows than available, read all rows with optimized settings
            df = pd.read_parquet(
                file_path,
                engine="pyarrow",
                use_threads=True,
                memory_map=True
            )
        else:
            # Read only the specified number of rows using batched reading
            batch = next(pf.iter_batches(batch_size=num_rows))
            df = pa.Table.from_batches(batches=[batch]).to_pandas()

    if sort_alphabetically:
        # Use inplace sorting if possible to avoid copying the entire dataframe
        df = df.reindex(sorted(df.columns), axis=1)

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
    # Create a copy only if we need to modify the dataframe
    columns_to_clean = []

    # First identify which columns need cleaning
    for col in df.columns:
        sample_values = df[col].dropna().astype(str)

        if not sample_values.empty and sample_values.str.startswith("$").all():
            columns_to_clean.append(col)

    # If no columns need cleaning, return the original dataframe
    if not columns_to_clean:
        return df

    # Only create a copy if we need to modify the dataframe
    new_df = df.copy()

    # Process only the columns that need cleaning
    for col in columns_to_clean:
        # Process in a single step to avoid intermediate copies
        new_df[col] = pd.to_numeric(df[col].astype(str).str[1:], errors="coerce")

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


def json_to_df(file_name: str, col_names: list) -> Any:
    """
    Converts a JSON file into a pandas DataFrame.

    This function reads a JSON file and converts its key-value pairs into
    a pandas DataFrame. Keys and values in the JSON are extracted and arranged
    into columns based on the provided column names. If the specified file
    does not exist, it raises a FileNotFoundError.

    Arguments:
        file_name: str
            The name of the JSON file to be loaded. Path is resolved under
            the `DATA_DIRECTORY`.
        col_names: list
            A list specifying the column names for the resulting DataFrame.
            The first column represents the keys, and the second represents
            the values from the JSON file.

    Returns:
        Any
            A pandas DataFrame containing data from the JSON file arranged
            in columns defined by `col_names`.

    Raises:
        FileNotFoundError
            If the specified JSON file does not exist in the resolved path.
    """
    json_path = DATA_DIRECTORY / file_name
    if not json_path.exists():
        raise FileNotFoundError(f"⚠️ JSON file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = list(data.items())
    return pd.DataFrame(items, columns=col_names)


def get_mcc_description_by_merchant_id(df_mcc: pd.DataFrame, merchant_id: int | str) -> str:
    """
    Fetch the Merchant Category Code (MCC) description associated with a given merchant ID from a DataFrame.
    If the merchant ID is invalid or not found in the DataFrame, returns "Undefined".

    Args:
        df_mcc (pd.DataFrame): A DataFrame with 'mcc' and 'merchant_group' columns.
        merchant_id (int | str): The merchant ID to lookup in the DataFrame.

    Returns:
        str: The MCC description associated with the given merchant ID, or "Undefined" if the ID is invalid or not found.
    """
    # Normalize merchant_id: Int->Str
    try:
        mcc_id = int(merchant_id)
    except (ValueError, TypeError):
        return "Undefined"

    # Lookup in DataFrame
    result = df_mcc[df_mcc['mcc'] == mcc_id]
    if len(result) > 0:
        return result.iloc[0]['merchant_group']
    else:
        return "Undefined"


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
