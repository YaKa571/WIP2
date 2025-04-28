from pathlib import Path

import pandas as pd

DATA_DIRECTORY = Path("assets/data/")


def read_csv_data(file_name: str, sort_alphabetically: bool = True, separator: str = ",",
                  encoding: str = "utf8") -> pd.DataFrame:
    """
    Reads a CSV file and returns its content as a pandas DataFrame.
    
    Args:
        file_name: Name of the CSV file to read
        sort_alphabetically: If True, sorts DataFrame columns alphabetically
        separator: CSV field separator character
        encoding: File encoding to use
        
    Returns:
        pandas DataFrame containing the CSV data
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
    """
    file_path = DATA_DIRECTORY / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    data_frame = pd.read_csv(
        file_path,
        sep=separator,
        encoding=encoding
    )

    if sort_alphabetically:
        data_frame = data_frame[sorted(data_frame.columns.tolist())]

    return data_frame
