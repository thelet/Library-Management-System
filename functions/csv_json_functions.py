"""
basic library of function to manipulate csv and json files.
"""

from typing import List, Dict, Any

import numpy as np
import pandas as pd
import csv
import json



def find_csv_separator(csv_file_path):
    """
    Detects the separator used in a CSV file.

    :param csv_file_path: The path to the CSV file.
    :return: The detected separator as a string.
    :raises RuntimeError: If the separator cannot be determined.
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            sample = csv_file.read(1024)  # Read the first 1KB of the file
            sniffer = csv.Sniffer()
            separator = sniffer.sniff(sample).delimiter
            return separator
    except Exception as e:
        raise RuntimeError(f"Failed to determine the separator for the CSV file: {csv_file_path}. Error: {e}")


def csv_to_json(csv_file_path, json_file_path, seperator= None):
    """
    Converts a CSV file into a JSON file.

    :param csv_file_path: str - Path to the input CSV file.
    :param json_file_path: str - Path to save the output JSON file.
    :param seperator: str or None - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If reading the CSV or writing the JSON fails.
    :raises Exception: If file path types mismatch or if seperator is None and cannot be determined from the file.

    :return: None
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path, json_file_path=json_file_path)

    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator).to_json(json_file_path, indent=1, orient='records')
        print(f"loaded csv file: {csv_file_path} \nto json file: {json_file_path} successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV to JSON. CSV file: {csv_file_path}, JSON file: {json_file_path}. Error: {e}")


def json_to_csv(json_file_path, csv_file_path, seperator=','):
    """
    Converts a JSON file into a CSV file.

    :param json_file_path: str - Path to the input JSON file.
    :param csv_file_path: str - Path to save the output CSV file.
    :param seperator: str or None - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If reading the JSON file or writing the CSV file fails.
    :raises Exception: If file path types mismatch or if seperator is None and cannot be determined from the file.

    :return: None
    """
    raise_args_exception(json_file_path=json_file_path, csv_file_path=csv_file_path)
    try:
        object_df = pd.read_json(json_file_path).to_csv(csv_file_path, sep=seperator, index=False)
        print(f"loaded json file: {json_file_path} \nto csv file: {csv_file_path} successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to convert JSON to CSV. JSON file: {json_file_path}, CSV file: {csv_file_path}. Error: {e}")


def get_csv_header(csv_file_path, seperator=None):
    """
    Retrieves the headers (column names) of a CSV file.

    :param csv_file_path: str - Path to the CSV file.
    :param seperator: str or None - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If reading the CSV file fails.
    :raises Exception: If file type mismatch or if seperator is None and cannot be determined from the file.

    :return: List[str] - A list of column names (headers) from the CSV file.
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path)
    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        return object_df.columns.values.tolist()
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve CSV headers. CSV file: {csv_file_path}. Error: {e}")


def add_to_csv(csv_file_path, new_data: List[str], seperator=None):
    """
    Adds a new row to a CSV file.

    :param csv_file_path: str - Path to the CSV file where the new data will be added.
    :param new_data: list[str] - A list representing the new row to be added.
        - Each element in the list corresponds to a column value in the CSV.
        - The order of the elements must match the existing column headers in the CSV file.
    :param seperator: str or None - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If adding new data to the CSV file fails.
    :raises Exception: If argument validation in `raise_args_exception` or `handle_args` fails.

    :return: None
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path, row=new_data)
    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        new_row_df = pd.DataFrame([new_data], columns=object_df.columns)
        updated_df = pd.concat([object_df, new_row_df], ignore_index=True)
        updated_df.to_csv(csv_file_path, sep=seperator, index=False)
        print(f"added new row to csv file: {csv_file_path} successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to add new rows to CSV file: {csv_file_path}. Error: {e}")


def delete_from_csv(csv_file_path, row_number, seperator=None):
    """
    Deletes a specific row from a CSV file.

    :param csv_file_path: str - Path to the CSV file.
    :param row_number: int - Index of the row to delete.
    :param seperator: str - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If deleting the row fails.

    :return: None
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path)
    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        object_df = object_df.drop(row_number)
        object_df.to_csv(csv_file_path, sep=seperator, index=False)
        print(f"Deleted row {row_number} from CSV file: {csv_file_path} successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to delete row from CSV file: {csv_file_path}. Row: {row_number}. Error: {e}")


def update_csv_row(csv_file_path, row_number: int, new_row: list, seperator=','):
    """
    Updates a specific row in a CSV file.

    :param csv_file_path: str - Path to the CSV file.
    :param row_number: int - Index of the row to update.
    :param new_row: list - The new row values to replace the existing row.
    :param seperator: str - CSV delimiter (default is ',').

    :raises RuntimeError: If updating the row fails.

    :return: None
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path, row=new_row)

    try:
        # Read the CSV into a DataFrame
        object_df = pd.read_csv(csv_file_path, sep=seperator)

        # Validate row index
        if row_number < 0 or row_number >= len(object_df):
            raise IndexError(f"Row index {row_number} is out of range. File has {len(object_df)} rows.")

        # Ensure the new row matches the DataFrame's column types
        for i, col in enumerate(object_df.columns):
            try:
                # Cast new_row[i] to the type of the corresponding column
                new_row[i] = object_df[col].dtype.type(new_row[i])
            except ValueError:
                raise ValueError(f"Value '{new_row[i]}' is incompatible with the dtype of column '{col}'.")

        # Update the row
        object_df.loc[row_number] = new_row

        # Save the updated DataFrame back to the CSV
        object_df.to_csv(csv_file_path, sep=seperator, index=False)
        print(f"Updated row {row_number} in CSV file: {csv_file_path} successfully.")
    except IndexError as e:
        raise RuntimeError(f"Row index out of range: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to update row in CSV file: {csv_file_path}. Row: {row_number}. Error: {e}")


def update_csv_cell(csv_file_path, row_number, column_header, new_value, seperator=None):
    """
    Updates a specific cell in a CSV file.

    :param csv_file_path: str - Path to the CSV file.
    :param row_number: int - Index of the row to update (0-based).
    :param column_header: str - The name of the column to update.
    :param new_value: Any - The new value to set in the specified cell.
    :param seperator: str - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If updating the cell fails.

    :return: None
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path, column_header=column_header)

    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)

        # Validate row index
        if row_number < 0 or row_number >= len(object_df):
            raise IndexError(f"Row index {row_number} is out of range. File has {len(object_df)} rows.")

        # Validate column header
        if column_header not in object_df.columns:
            raise ValueError(f"Column '{column_header}' does not exist in the CSV file.")

        # Cast new_value to the column's data type
        column_dtype = object_df[column_header].dtype
        if pd.api.types.is_numeric_dtype(column_dtype):
            new_value = pd.to_numeric(new_value, errors='coerce')
        elif pd.api.types.is_datetime64_any_dtype(column_dtype):
            new_value = pd.to_datetime(new_value, errors='coerce')
        else:
            new_value = str(new_value)

        # Update the cell
        object_df.loc[row_number, column_header] = new_value
        object_df.to_csv(csv_file_path, sep=seperator, index=False)
        print(f"Updated cell ({row_number}, {column_header}) in CSV file: {csv_file_path} successfully.")
    except IndexError as e:
        raise RuntimeError(f"Row index out of range: {e}")
    except ValueError as e:
        raise RuntimeError(f"Invalid column or value: {e}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to update cell in CSV file: {csv_file_path}. Row: {row_number}, Column: {column_header}. Error: {e}")


def get_csv_row(csv_file_path, row_number:int, seperator=None):
    """
    Retrieves a specific row from a CSV file by its row index.

    :param csv_file_path: str - Path to the CSV file.
    :param row_number: int - Index of the row to retrieve (0-based).
    :param seperator: str or None - CSV delimiter (default is None, assumes ',').

    :raises RuntimeError: If the row index is out of range or the operation fails.

    :return: pandas.Series - The requested row as a Series object.
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path)

    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        # Validate row index
        if row_number < 0 or int(row_number) >= len(object_df):
            raise IndexError(f"Row index {row_number} is out of range. File has {len(object_df)} rows.")
        row = object_df.iloc[row_number]
        return [value.item() if isinstance(value, (np.integer, np.floating)) else value for value in row.tolist()]
    except IndexError as e:
        raise RuntimeError(f"Row index out of range: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve row from CSV file: {csv_file_path}. Row: {row_number}. Error: {e}")



def get_csv_cell(csv_file_path, row_number, column_name, seperator=None):
    """
    Retrieves a specific cell from a CSV file.

    :param csv_file_path: str - Path to the CSV file.
    :param row_number: int - Index of the row containing the cell (0-based).
    :param column_name: str - Column name of the cell to retrieve.
    :param seperator: str or None - CSV delimiter (if None, it will be detected automatically).

    :raises RuntimeError: If retrieving the cell fails.

    :return: Any - The value of the requested cell.
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path=csv_file_path, column_header=column_name)
    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        return object_df.loc[row_number, column_name]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve cell from CSV file: {csv_file_path}. Row: {row_number}, Cell: {column_name}. Error: {e}")


def find_row_csv(csv_file_path, key : tuple[str, str], seperator=None):
    """
    Finds rows in a CSV file where a specific column matches a given value.

    :param csv_file_path: str - The path to the CSV file.
    :param key: tuple[str, str] - A tuple containing:
        - The column name (str) to search in.
        - The value (str) to match in the specified column.
    :param seperator: str - The delimiter used in the CSV file (if None, it will be detected automatically).
    :return: 2 list- -
        1- all rows where the specified column matches the given value.
        2- the row numbers of the matching rows.
    :raises RuntimeError: If the function fails to read the file or perform the operation, a detailed error is raised.
    """
    seperator = handle_args(seperator=seperator, csv_file_path=csv_file_path)
    raise_args_exception(csv_file_path= csv_file_path)
    try:
        object_df = pd.read_csv(csv_file_path, sep=seperator)
        matching_rows = object_df.loc[object_df[key[0]] == key[1]]
        row_numbers = matching_rows.index.tolist()
        matching_rows = matching_rows.values.tolist()
        return matching_rows, row_numbers
    except Exception as e:
        raise RuntimeError(f"Failed to find row by key in CSV file: {csv_file_path}. Key: {key}. Error: {e}")


def json_to_csv_row(csv_headers: List[str] or str, json_data: Dict[str, Any], ignore_missing_keys=None):
    """
    Converts JSON data into a CSV row, matching the provided headers.

    :param csv_headers: List[str] or str
        - If List[str], it represents the headers for the CSV.
        - If str, it is the path to a CSV file from which the headers will be derived.
    :param json_data: Dict[str, Any]
        - A dictionary representing the JSON data to be converted.
    :param ignore_missing_keys: bool or None (optional, default is false)
        - If True, the function will replace missing keys with empty strings in the CSV row.
        - If False or None, an exception will be raised if keys in `csv_headers` are not present in `json_data`.
    :return: List[str]
        - A list representing a CSV row, with values ordered according to `csv_headers`.

    :raises RuntimeError:
        - If the function fails to process the JSON data or map it to the headers.
    :raises Exception:
        - If `csv_headers` is not valid or keys in `json_data` doesn't match the keys in header  `ignore_missing_keys` is not True.
    """
    raise_args_exception(json_data=json_data, header=csv_headers, ignore_missing_keys=ignore_missing_keys)
    csv_headers = handle_args(csv_headers, get_header=True)
    try:
        csv_row = [str(json_data.get(header, "")) for header in csv_headers]
        return csv_row
    except Exception as e:
        raise RuntimeError(f"Failed to convert JSON data to CSV row. Headers: {csv_headers}. Error: {e}")


def csv_row_to_json(csv_headers: List[str] or str, csv_row: List[str]) -> Dict[str, Any]:
    """
    Converts a CSV row into a JSON-like dictionary using the provided headers.

    Args:
        csv_headers (List[str]): List of CSV header names.
        csv_row (List[str]): List of CSV row values.

    Returns:
        Dict[str, Any]: A dictionary representing the row as JSON.
    """
    try:
        if type(csv_headers) is not list[str]:
            print(f"finding headers from csv file {csv_headers}")
            csv_headers = get_csv_header(csv_headers)
        print(csv_headers)

        if len(csv_headers) != len(csv_row):
            print(f"IndexError: Row size {len(csv_row)} doesn't match CSV headers size {len(csv_headers)}")

        return {header: value for header, value in zip(csv_headers, csv_row)}
    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV row to JSON. Headers: {csv_headers}, Row: {csv_row}. Error: {e}")




def raise_args_exception(csv_file_path=None, json_file_path=None, header: List[str] = None,
                         row: List[str] = None, json_data: Dict[str, Any] = None, ignore_missing_keys = False,
                         column_header = None):
    #validate path
    if csv_file_path and not csv_file_path.endswith(".csv"):
        raise RuntimeError(f"Error: {csv_file_path} is not a CSV file")
    if json_file_path and not json_file_path.endswith(".json"):
        raise RuntimeError(f"Error: {json_file_path} is not a JSON file")
    #validate data length
    if csv_file_path and row and len(row) != len(get_csv_header(csv_file_path)):
        raise RuntimeError(f"Error: Row length {len(row)} doesn't match header length {len(get_csv_header(csv_file_path))}\n")
    if not ignore_missing_keys and header and len(header) > len(row):
        raise RuntimeError(f"Error: Header length {len(header)} doesn't match row length {len(row)}\n"
                           f"To ignore this error, set arg ignore_missing_keys to True")
    if json_data and len(json_data) != len(header):
        raise RuntimeError(f"JSON data length {len(json_data)} doesn't match header length {len(header)}\n"
                           f"Wrap  this ")
    #validate data existence
    if column_header and column_header not in get_csv_header(csv_file_path):
        raise ValueError(f"Column '{column_header}' does not exist in the CSV file.")


def handle_args(csv_file_path, seperator = None, get_header=False):
    #returns headers if needed
    if get_header:
        if type(csv_file_path) is not list[str]:
            return get_csv_header(csv_file_path, seperator)
        else:
            return csv_file_path
    #finds the seperator arg if it wasn't given
    elif seperator is None:
        try:
            seperator = find_csv_separator(csv_file_path)
        except Exception as e:
            raise RuntimeError(f"Error: {e}\n Try to provide seperator as an arg")
    return seperator


def main():
    csv_file = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data\books.csv"
    json_file = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data\books.json"
    csv_to_json(csv_file, json_file)














