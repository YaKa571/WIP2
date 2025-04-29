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


data_frame_users, units_users = clean_units(read_csv_data("users_data.csv", sort_alphabetically=False))
data_frame_transactions, units_transactions = clean_units(
    read_csv_data("transactions_data.csv", sort_alphabetically=False))
data_frame_cards, units_cards = clean_units(read_csv_data("cards_data.csv", sort_alphabetically=False))

print("\nℹ️ Information")
print(f"Users: {units_users}")
print(f"Transactions: {units_transactions}")
print(f"Cards: {units_cards}")
print()
