import ast
import csv
import os
import json
from typing import List, Optional, Union, Any

count_runs = 0
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
    "borrow_count": "borrow_count"
}


def write_json_obj(obj_list : 'Book' or 'User', json_root :str, obj_name :str):
    global count_runs
    count_runs += 1
    """
    Creates a new directory called 'books_json' within the given root_dir.
    For each Book in 'books', writes a JSON file named '{book.id}.json' 
    containing the book's data.

    :param books: List of Book objects, each having a to_json() method.
    :param root_dir: The path to the existing root directory.
    """
    # Name for the new subdirectory
    new_dir_name = f"{obj_name}_json"

    # Construct full path for the new directory
    new_dir_path = os.path.join(json_root, new_dir_name)

    # Create the new directory (if it doesn't exist)
    os.makedirs(new_dir_path, exist_ok=True)

    # Iterate over each book and write its JSON file
    for obj in obj_list:
        # The file name is the book's id followed by '.json'
        file_name = f"{obj.id}.json"
        file_path = os.path.join(new_dir_path, file_name)

        # Convert book to JSON dictionary
        obj_data = obj.to_json()

        # Write the JSON data to the file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(obj_data, json_file, indent=4)

    print(f"Exported {len(obj_list)} {obj_name} to JSON files in '{new_dir_path}'.")

def load_json_obj(json_path, obj_name :str):
    from Classes.user import User
    from Classes.book import Book
    if json_path.endswith(".json"):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if obj_name == "users":
                    return User.from_json(data)
                elif obj_name == "books":
                    return Book.from_json(data)
                else:
                    raise ValueError("Invalid object name")

        except Exception as e:
            print(f"Failed to load obj {json_path}: {e}")

def load_objs_from_json(json_dir: str, obj_name :str, ids: Optional[List[Union[int, str]]] = None) -> dict[int, Any]:
    """
    Loads obj from JSON files in the given directory.

    1) If 'ids' is None, the function loads **all** .json files in 'json_dir'.
    2) If 'ids' is a list, it attempts to load only those IDs (matching {id}.json filenames).

    :param json_dir: Path to the directory containing obj JSON files (named like '123.json').
    :param ids: Either a list of IDs (e.g., [123, 456]) or None to load all.
    :param obj_name: Name of the object to load.
    :return: A list of obj (books or users) objects.
    """
    from Classes.user import User
    from Classes.book import Book

    loaded_obj : dict[int, User] or dict[int, Book] = {}

    # Case 1: No specific IDs => load all JSON files in the directory
    if ids is None:
        #try:
            for file_name in os.listdir(json_dir):
                loaded = load_json_obj(os.path.join(json_dir, file_name), obj_name)
                if loaded:
                    loaded_obj[loaded.id] = loaded
                else:
                    print(f"Failed to load obj {file_name}")
        #except Exception as e:
        #    print(f"Error {json_dir}: {e}")

    # Case 2: We have a list of specific IDs => load only those IDs
    else:
        for o_id in ids:
            # Convert b_id to string if needed, to match file naming convention
            file_name = f"{ids}.json"
            file_path = os.path.join(json_dir, file_name)

            if os.path.exists(file_path):
                try:
                    new_book = load_json_obj(file_path, obj_name)
                    loaded_obj[new_book.id] = new_book
                except Exception as e:
                    print(f"Failed to load obj with ID '{o_id}': {e}")
            else:
                print(f"File not found for obj ID '{o_id}' => {file_path}")

    return loaded_obj

def reattached_observers(books_dict : dict[int ,'Book'], users_dict : dict[int, 'User']):
    for loaded_book in books_dict.values():
        if len(loaded_book.temp_followers) > 0:
            temp_followers = loaded_book.temp_followers
            not_found = []
            for user_id in temp_followers:
                print(f"searching for user: {user_id}")
                if user_id in users_dict:
                    loaded_book.user_observers.append(users_dict[user_id])
                    print(f" found user: {user_id}, left users: {temp_followers}")
                else:
                    print(f"User {user_id} not found")
                    not_found.append(user_id)
            loaded_book.temp_followers = not_found

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









def jsons_to_csv_with_mapping(json_dir, csv_file_path, headers_mapping):
    """
    Converts all JSON files in a directory to a single CSV file, using a specified mapping of JSON fields to CSV headers.

    :param json_dir: str - Directory containing JSON files.
    :param csv_file_path: str - Path to save the consolidated CSV file.
    :param headers_mapping: dict - Mapping of JSON field names to CSV header names (e.g., {"json_field": "csv_header"}).
    """
    try:
        # Extract CSV headers from the mapping
        csv_headers = list(headers_mapping.values())

        # Prepare data for writing
        data = []
        for file_name in os.listdir(json_dir):
            if file_name.endswith(".json"):
                json_path = os.path.join(json_dir, file_name)
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                    # Check if all required JSON fields are present
                    if all(field in json_data for field in headers_mapping.keys()):
                        # Map JSON fields to CSV fields using the headers_mapping
                        data.append(
                            {csv_header: json_data[json_field] for json_field, csv_header in headers_mapping.items()})
                    else:
                        missing_fields = [field for field in headers_mapping.keys() if field not in json_data]
                        print(f"Skipping file {file_name}: Missing required fields {missing_fields}.")

        # Write to CSV
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            writer.writeheader()  # Write headers
            for row in data:
                writer.writerow(row)

        print(f"JSON files have been successfully consolidated into: {csv_file_path}")

    except Exception as e:
        raise RuntimeError(f"Failed to consolidate JSON files into CSV. Error: {e}")



def csv_to_individual_json_files(csv_file_path, headers_mapping, output_dir, id_field="id"):
    """
    Converts a CSV file to individual JSON files using a headers mapping.
    Each JSON file will be named based on the `id_field`.

    :param csv_file_path: str - Path to the input CSV file.
    :param headers_mapping: dict - A mapping where the key is the CSV header and the value is the JSON key.
    :param output_dir: str - Root directory to save the individual JSON files.
    :param id_field: str - The field to use for naming JSON files (default is "id").
    :return: None
    """

    keys_to_list = ["user_observers", "borrowed_books", "previously_borrowed_books"]
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    # Map the row to the JSON structure
                    mapped_row = {}
                    for json_key, csv_header in headers_mapping.items():
                        if csv_header in row:
                            value = row[csv_header]
                            # Preserve original types
                            if value.isdigit():
                                value = int(value)
                            else:
                                try:
                                    value = float(value)
                                except ValueError:
                                    pass  # Leave as string if not int/float
                            mapped_row[json_key] = value
                        else:
                            raise KeyError(f"Missing CSV header: {csv_header} , for id: {row['id']}")

                    # Ensure the `id_field` exists for naming the file
                    if id_field not in mapped_row:
                        raise KeyError(f"ID field '{id_field}' is missing in the row: {row}")

                    # Create the JSON file name
                    json_file_name = f"{mapped_row[id_field]}.json"
                    json_file_path = os.path.join(output_dir, json_file_name)

                    # Write the JSON file
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        for list_key in keys_to_list:
                            if list_key in mapped_row:
                                mapped_row[list_key] = ast.literal_eval(mapped_row[list_key])
                        json.dump(mapped_row, json_file, indent=4)

                    print(f"Written: {json_file_path}")

                except OSError as e:
                    print(f"missing key: {e}")
                    continue
    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV to individual JSON files. Error: {e}")


def json_test_main():
    from Classes.book import Book
    from Classes.user import User, Librarian

    json_root = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data"

    book3= Book.createBook("title3", "author3", 2003, "category3", 3)
    book4 = Book.createBook("title4", "author4", 2004, "category4", 4)
    book5 = Book.createBook("title5", "author5", 2005, "category5", 5)
    book_set = (book3, book4)
    print(f"\ncreated books:\n")
    for book in book_set:
        print(book, end="")

    user1 = User.create_user(username="user1", passwordHash="password1")
    user2 = User.create_user(username="user2", passwordHash="password2")
    user3 = Librarian.create_librarian(username="user3", passwordHash="password3")
    user4 = User.create_user(username="user4", passwordHash="password4")
    user_set = (user1, user2, user3)
    print(f"\ncreated users: \n")
    for user in user_set:
        print(user, end="")

    book3.attach(user1)
    book3.attach(user2)
    book4.attach(user3)
    book3.attach(user4)
    user1.borrowedBooks.append(book5)
    user1.borrowedBooks.append(book4)
    user3.borrowedBooks.append(book3)
    user2.borrowedBooks.append(book4)
    user2.borrowedBooks.append(book3)


    write_json_obj(book_set,json_root, "books")

    json_books_to_load = os.path.join(json_root, "books_json_1")
    loaded_books = load_objs_from_json(json_books_to_load, "books")
    print(f"\nLoaded books: \n")
    for book in loaded_books.values():
          print(book.__str__(), end = "")


    write_json_obj(user_set, json_root, "users")

    json_users_to_load = os.path.join(json_root, "users_json_2")
    loaded_users = load_objs_from_json(json_users_to_load, "users")
    print(f"\nLoaded users: \n")
    for user in loaded_users.values():
        print(user.__str__(), end = "")

    reattached_observers(loaded_books, loaded_users)

    for book in loaded_books:
        print(f"\nid: {book} \nfollowers: \n{[user_obs.id for user_obs in loaded_books[book].user_observers]} \n"
              f"temp_followers: {loaded_books[book].temp_followers}")

    reconnect_borrowed_books(loaded_users, loaded_books)

    for user in loaded_users.values():
        print(f"\nid: {user.id} \nborrowed_books: \n{[book.id for book in user.borrowedBooks]}\ntemp books: \n{user.temp_borrowedBooks}")

    csv_root = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data"
    jsons_to_csv_with_mapping(json_users_to_load, os.path.join(csv_root, "users_2.csv"), user_headers_mapping)
    jsons_to_csv_with_mapping(json_books_to_load, os.path.join(csv_root, "books_1.csv"), book_headers_mapping)

def csv_test_main():
    csv_root = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data"
    json_books =r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data\books_from_csv"
    json_users = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data\users_from_csv"
    csv_to_individual_json_files(os.path.join(csv_root, "books_1.csv"),book_headers_mapping,json_books)
    csv_to_individual_json_files(os.path.join(csv_root, "users_2.csv"),user_headers_mapping,json_users)

    book_dict = load_objs_from_json(json_books, "books")
    print(f"\nLoaded books: \n")
    for book in book_dict.values():
        print(book.__str__(), end="")

    user_dict = load_objs_from_json(json_users, "users")
    print(f"\nLoaded users: \n")
    for user in user_dict.values():
        print(user.__str__(), end="")

    reattached_observers(book_dict, user_dict)
    for book in book_dict:
        print(f"\nid: {book} \nfollowers: \n{[user_obs.id for user_obs in book_dict[book].user_observers]} \n"
              f"temp_followers: {book_dict[book].temp_followers}")

    reconnect_borrowed_books(user_dict, book_dict)

    for user in user_dict.values():
        print(f"\nid: {user.id} \nborrowed_books: \n{[book.id for book in user.borrowedBooks]}\ntemp books: \n{user.temp_borrowedBooks}")

def test_new_list():
    from Classes.library import Library

    book1 = Book.createBook("title1", "author1", 2001, "category1", 1)
    book2 = Book.createBook("title2", "author2", 2002, "category2", 2)
    book3 = Book.createBook("title3", "author3", 2003, "category3", 3)
    book4 = Book.createBook("title4", "author4", 2004, "category4", 4)
    book5 = Book.createBook("title5", "author5", 2005, "category5", 5)
    book11 =Book.createBook("title6", "author1", 2006, "category6", 6)
    book12 = Book.createBook("title7", "author7", 2007, "category1", 7)
    book13 = Book.createBook("title8", "author1", 2008, "category1", 3)
    book14 = Book.createBook("title1", "author8", 2003, "category8", 3)
    book9 = Book.createBook("title9", "author1", 2001, "category1", 1)
    book10 = Book.createBook("title10", "author2", 2002, "category2", 2)
    book15 = Book.createBook("title11", "author3", 2003, "category3", 3)
    book16 =Book.createBook("title16", "author1", 2006, "category6", 6)
    book17 = Book.createBook("title17", "author7", 2007, "category1", 7)
    book18 = Book.createBook("title18", "author1", 2008, "category1", 3)
    books = [book1, book2, book3, book4, book5, book11, book12, book13, book14, book9, book10, book15, book16, book17, book18]

    user1 = User.create_user(username="user1", passwordHash="password1")
    user2 = User.create_user(username="user2", passwordHash="password2")
    user3 = Librarian.create_librarian(username="user3", passwordHash="password3")
    user4 = User.create_user(username="user4", passwordHash="password4")
    users = [user1, user2, user3, user4]

    book3.attach(user1)
    book3.attach(user2)
    book4.attach(user3)
    book3.attach(user4)
    book5.attach(user1)
    user1.borrowedBooks.append(book5)
    user1.borrowedBooks.append(book17)
    user1.borrowedBooks.append(book11)
    user1.borrowedBooks.append(book4)
    user3.borrowedBooks.append(book3)
    user3.borrowedBooks.append(book9)
    user2.borrowedBooks.append(book4)
    user2.borrowedBooks.append(book3)
    book5.set_borrow_count(7)
    book17.set_borrow_count(1)
    book11.set_borrow_count(1)
    book4.set_borrow_count(2)
    book1.set_borrow_count(9)
    book2.set_borrow_count(8)
    book3.set_borrow_count(6)
    book9.set_borrow_count(1)
    book10.set_borrow_count(10)
    book15.set_borrow_count(13)
    book16.set_borrow_count(16)
    book18.set_borrow_count(1)
    for user in users:
        print(user)

    user1.returnBook(book5)
    user2.returnBook(book3)
    user1.returnBook(book4)

    for user in users:
        print(f"id: {user.id} | borrowed_books: {[book.id for book in user.borrowedBooks]} | previously borrowed {user.previously_borrowed_books}\n")

    json_root = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data"
    csv_root = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\CSV_data"
    write_json_obj(users, json_root, "users")
    write_json_obj(books, json_root, "books")
    json_users = os.path.join(json_root, "users_json")
    json_books = os.path.join(json_root, "books_json")
    jsons_to_csv_with_mapping(json_users, os.path.join(csv_root, "users_1.csv"), user_headers_mapping)
    jsons_to_csv_with_mapping(json_books, os.path.join(csv_root, "books_1.csv"), book_headers_mapping)
    json_users = os.path.join(json_root, "users_json_from_csv")
    json_books = os.path.join(json_root, "books_json_from_csv")
    csv_to_individual_json_files(os.path.join(csv_root, "users_1.csv"), user_headers_mapping, json_users)
    csv_to_individual_json_files(os.path.join(csv_root, "books_1.csv"), book_headers_mapping, json_books)
    books_dict = load_objs_from_json(json_books, "books")
    users_dict = load_objs_from_json(json_users, "users")
    reattached_observers(books_dict, users_dict)
    reconnect_borrowed_books(users_dict, books_dict)
    for user in users_dict.values():
        print(f"id: {user.id} | borrowed_books: {[book.id for book in user.borrowedBooks]} "
              f"| previously borrowed {user.previously_borrowed_books} | temp books: {user.temp_borrowedBooks}\n")

    for book in books_dict.values():
        print(book)



if __name__ == '__main__':
    from Classes.book import Book
    from Classes.user import User, Librarian
    test_new_list()





