import csv
import os
from typing import Any, Dict
import json

user_headers_mapping = {
    "id": "user_id",
    "username": "username",
    "passwordHash": "password",
    "borrowed_books" : "borrowed_books"  ,
    "role": "role",
    "previously_borrowed_books" : "previously_borrowed_books"
}

book_headers_mapping = {
    "id": "id",
    "title": "title",
    "author": "author",
    "year": "year",
    "category": "genre",
    "copies": "copies",
    "isLoaned": "is_loaned",
    "user_observers": "followers_ids",
    "borrow_count": "borrow_count",
    "borrowed_users" : "borrowed_users",
}

book_deco_headers_mapping = {
    "id": "id",
    "type": "type",
    "decorator" : "decorator"
}



def check_csv_headers(csv_file_path: str, required_headers: list[str]) -> bool:
    """
    Checks if the CSV file at 'csv_file_path' contains all 'required_headers'.

    :param csv_file_path: The path to the CSV file.
    :param required_headers: A list of headers that must be present in the CSV.
    :return: True if the CSV contains all required headers.
    :raises ValueError: If one or more required headers are missing. The error message
                        will include the CSV headers, the required headers, and the missing headers.
    """
    with open(csv_file_path, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        csv_headers = reader.fieldnames

        # If CSV is empty or has no header row, fieldnames might be None
        if not csv_headers:
            csv_headers = []

        missing_headers = [hdr for hdr in required_headers if hdr not in csv_headers]

        if missing_headers:
            raise ValueError(
                f"CSV is missing required header(s): {missing_headers}. "
                f"CSV Headers: {csv_headers}. "
                f"Required Headers: {required_headers}."
            )

    return True


def load_objs_dict_from_csv(csv_file_path: str, headers_mapping: dict[str, str], obj_type: str) -> dict[int, Any]:
    """
    Loads objects from a CSV file by mapping CSV headers to the keys expected by
    an object's from_json method.

    :param csv_file_path: Path to the CSV file containing object data.
    :param headers_mapping: A dict where:
                           - KEY = the parameter name your object’s from_json expects
                           - VALUE = the CSV column header containing the corresponding data
    :param obj_type: The type of the objects that will be returned checked.
    :return: A list of objects instantiated by calling the from_json method.
    :raises ValueError: If a required CSV header is missing (re-raised from check_csv_headers).
    """
    if obj_type == "Book":
        modify_csv(csv_file_path)
    # 1. Ensure the CSV has all headers required by headers_mapping.values()
    check_csv_headers(csv_file_path, list(headers_mapping.values()))

    objects = {}
    with open(csv_file_path, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            # 2. Build a dict that maps the object's keys to row values
            json_data = {}
            for obj_key, csv_header in headers_mapping.items():
                json_data[obj_key] = row[csv_header]

            if obj_type == 'User':
                from Classes.user import User
                obj_instance = User.from_json(json_data)
            elif obj_type == 'Book':
                from Classes.book import Book
                obj_instance = Book.from_json(json_data)
            else:
                raise ValueError(f"Error while loading users from csv: unknown obj type : {obj_type}")

            objects[obj_instance.id] = obj_instance

    return objects

def modify_csv(file_path: str):
    """
    Modify the CSV file in place to fit the required structure:
      - If there's no 'id' header, create it with int values = row number (1-based).
      - 'title', 'genre', 'copies', 'year', 'is_loaned' headers remain the same if they exist.
      - If there's no 'followers_ids' column, create it and fill with "[]".
      - If there's no 'borrow_count' column, create it:
           if is_loaned == "Yes" => borrow_count = copies
           else => borrow_count = 0
      - Preserve all other existing columns/values.
    """

    required_fields = [
        "id",
        "title",
        "genre",
        "copies",
        "year",
        "is_loaned",
        "followers_ids",
        "borrow_count",
        "borrowed_users"
    ]

    # Read the original CSV
    with open(file_path, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        original_fieldnames = list(reader.fieldnames) if reader.fieldnames else []

        # Determine which required fields are missing
        missing_fields = [f for f in required_fields if f not in original_fieldnames]

        # Create a new fieldnames list that combines original + any missing
        new_fieldnames = original_fieldnames + missing_fields

        rows = []
        for i, row in enumerate(reader, start=1):
            # If 'id' is missing or empty in the original, set it
            if "id" not in row or not row["id"].strip():
                print(f"adding id to row {i}")
                row["id"] = i

            # If 'followers_ids' is missing or empty, set it to "[]"
            if "followers_ids" not in row or not row["followers_ids"].strip():
                print(f"adding followers_ids to row {i}")
                row["followers_ids"] = []

            if not row.get("borrowed_users", "").strip():
                if row["is_loaned"] == "Yes":
                    row["borrowed_users"] = [0] * int(row.get("copies", "0").strip())
                else:
                    row["borrowed_users"] = []

            # If 'borrow_count' is missing, calculate based on 'is_loaned' and 'copies'
            if "borrow_count" not in row or not row["borrow_count"]:
                    row["borrow_count"] = 0

            # Make sure that missing columns (from new_fieldnames) are set to empty if not present
            for field in missing_fields:
                if field not in row:
                    row[field] = ""

            # Convert all new numeric fields to string for writing consistency
            if isinstance(row.get("id"), int):
                row["id"] = str(row["id"])
            if isinstance(row.get("borrow_count"), int):
                row["borrow_count"] = str(row["borrow_count"])

            rows.append(row)

    # Write the updated CSV with both original and newly added columns
    with open(file_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def connect_books_and_users(users: dict[int ,'User'], books: dict[int ,'Book']):
    reconnect_borrowed_books(users, books)
    reattached_observers(books, users)
    connect_lost_books(books, users)
    print("finished connecting books and users")



def reconnect_obs_list(ids_list, obj_dict: dict[int, 'User'] or dict[int, 'Book']):
    obj_list = []
    not_found = []
    for o_id in ids_list:
        if o_id in obj_dict:
            obj_list.append(obj_dict[o_id])
        else:
            not_found.append(o_id)
    return obj_list, not_found

def reconnect_borrowed_books(users_dict : dict[int, 'User'], books_dict: dict[int, 'Book']):
    for user in users_dict.values():
        books_list, not_found = reconnect_obs_list(user.temp_borrowedBooks, books_dict)
        user.borrowedBooks = books_list
        user.temp_borrowedBooks = not_found
        print(f"users not found when trying to connect books: {not_found}")

def reattached_observers(books_dict : dict[int ,'Book'], users_dict : dict[int, 'User']):
    from Classes.library import Library
    for loaded_book in books_dict.values():
        if len(loaded_book.temp_followers) > 0:
            temp_followers = loaded_book.temp_followers
            not_found = set()
            for user_id in temp_followers:
                print(f"searching for user: {user_id}")
                if user_id in users_dict:
                    loaded_book.user_observers.append(users_dict[user_id])
                    print(f" found user: {user_id}, left users: {temp_followers}")
                else:
                    print(f"Warning: User {user_id} not found")
                    not_found.add(user_id)
            loaded_book.temp_followers = not_found


def connect_lost_books(books_dict : dict[int, 'Book'], users_dict : dict[int, 'User']):
    from Classes.library import Library
    for book in books_dict.values():
        lib = Library.getInstance()
        # for the template csv, that didn't contain the id's for the users who borrowed the book.
        # we attach the books to a dedicated library user in order to be able to test on them.
        for use_id in book.borrowed_users:
            if use_id == 0 or use_id not in users_dict.keys():
                print(f"user: {use_id} not found, attaching lost book {book.title}")
                book.updateCopies(1)
                book.borrowed_users.remove(use_id)
                lib.lendBook(lib.lost_books_user, book)
        print(book)
        lib.logger.log(f"{book.__str__()}")

def create_empty_files(csv_file_path, headers_list, file_name_adder :str):
    # Split the original file into base (without extension) and the extension
    if csv_file_path:
        base, ext = os.path.splitext(csv_file_path)
        # Construct the new file path by appending '_users' before the extension
        new_file_path = base + file_name_adder + ext
    else:
        # Use the current working directory as the project directory
        project_dir = os.getcwd()
        # Define the new file name
        new_file_name = file_name_adder + ".csv"
        # Construct the new file path
        new_file_path = os.path.join(project_dir, new_file_name)

    # Create and write the new CSV file
    with open(new_file_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers_list)
        writer.writeheader()

    return new_file_path




def upsert_obj_to_csv(
        obj_data: Dict[str, Any],
        csv_file_path: str,
        headers_mapping: Dict[str, str]
) -> None:
    """
    Updates an existing row in the CSV if 'id' matches, otherwise appends a new row.
    :param obj_data: A dictionary containing the object's data.
    :param csv_file_path: Path to the existing CSV file.
    :param headers_mapping: A mapping where:
                            - Key = The object's dict key.
                            - Value = The corresponding CSV header.
    :raises ValueError: If the CSV file lacks required headers.
    :raises IOError: If there's an issue reading or writing to the CSV file.
    """
    try:
        # Step 1: Read all existing rows
        with open(csv_file_path, mode='r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            existing_headers = reader.fieldnames

            if existing_headers is None:
                raise ValueError(f"The CSV file '{csv_file_path}' has no headers.")

            # Verify that all required headers are present
            missing_headers = [header for header in headers_mapping.values() if header not in existing_headers]
            if missing_headers:
                raise ValueError(
                    f"CSV is missing required header(s): {missing_headers}. "
                    f"Existing Headers: {existing_headers}."
                )

            # Read all rows into a list
            rows = list(reader)

        # Step 2: Prepare the new row data
        row_data = {}
        for obj_key, csv_header in headers_mapping.items():
            value = obj_data.get(obj_key, "")
            # Serialize lists and dictionaries to JSON strings
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            row_data[csv_header] = value

        # Step 3: Determine the 'id' header and the object 'id' value
        id_header = headers_mapping.get('id')
        if not id_header:
            raise ValueError("Headers mapping must include a mapping for 'id'.")

        obj_id = str(obj_data.get('id', '')).strip()
        if not obj_id:
            raise ValueError("Object data must include a non-empty 'id'.")

        # Step 4: Search for an existing row with the same 'id'
        row_found = False
        for index, row in enumerate(rows):
            if row.get(id_header, '').strip() == obj_id:
                # Overwrite the existing row
                rows[index] = row_data
                row_found = True
                print(f"Updated existing row with id={obj_id}.")
                break

        if not row_found:
            # Append the new row
            rows.append(row_data)
            print(f"Appended new row with id={obj_id}.")

        # Step 5: Write all rows back to the CSV
        with open(csv_file_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=existing_headers)
            writer.writeheader()
            writer.writerows(rows)

    except FileNotFoundError:
        raise FileNotFoundError(f"The CSV file '{csv_file_path}' does not exist.")
    except IOError as e:
        raise IOError(f"An I/O error occurred: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def get_decorator_from_dict(self, deco_dict : Dict[str, Any]):
    from Classes.library import Library
    from decorator import CoverDecorator, DescriptionDecorator

    lb = Library().getInstance()
    if int(deco_dict['id']) not in lb.books.keys():
        print(f"Warning: Book {deco_dict['id']} not found, when it's decorator exist")
        return None

    deco_book = lb.books[int(deco_dict['id'])]
    if "cover_image" in deco_dict.keys():
        d_book = CoverDecorator(deco_book, deco_dict["cover_image"])
    elif "description" in deco_dict.keys():
        d_book = DescriptionDecorator(deco_book, deco_dict["description"])


def main():
    from Classes.user import User
    from Classes.book import Book
    from Classes.library import Library
    lb = Library().getInstance()

    books_csv_path = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data\books.csv"
    #users_csv_path =r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data\users_1.csv"

    books_dictionary = load_objs_dict_from_csv(books_csv_path, book_headers_mapping, "Book")
    for obj_id, obj in books_dictionary.items():
        print(f"{obj_id} : {obj}")
    #users_dictionary = load_objs_dict_from_csv(users_csv_path, user_headers_mapping, "User")
    #for obj_id, obj in users_dictionary.items():
    #    print(f"{obj_id} : {obj}")

    user1 = User("lost_books", "00000")
    user2 = User.create_user("user2", "11111")
    lb.lendBook(user2, books_dictionary[1])
    print(f"book 1: {books_dictionary[1]}")
    users = {0: user1}
    connect_books_and_users(users, books_dictionary)
    for obj_id, obj in books_dictionary.items():
        print(f"{obj_id} : {obj}")
    #for obj_id, obj in users_dictionary.items():
    #    print(f"{obj_id} : {obj}")



if __name__ == "__main__":
    main()