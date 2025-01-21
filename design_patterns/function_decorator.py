from functools import wraps
from design_patterns.exceptions import PermissionDeniedException
import functools
import inspect
from manage_files import csv_manager

def permission_required(permission: str):
    """
    A decorator to check if the caller (user) has the required permission before executing the function.

    :param permission: The required permission as a string.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Assuming the caller (user) is passed as the first argument
            caller = args[0]

            if not hasattr(caller, "has_permission"):
                raise AttributeError("Caller object must have a 'has_permission' method.")

            if not caller.has_permission(permission):
                print(caller)
                raise PermissionDeniedException(f"Permission '{permission}' required to perform this action.")

            # Execute the original function if permission check passes
            return func(*args, **kwargs)

        return wrapper

    return decorator



def upsert_after(obj_arg_name, csv_file_path_attr, headers_mapping_attr):
    """
    Decorator to perform an upsert operation after the decorated function executes successfully.

    :param obj_arg_name: The name of the argument that contains the object data.
    :param csv_file_path_attr: The name of the attribute in 'self' that holds the CSV file path.
    :param headers_mapping_attr: The name of the attribute in 'self' that holds the headers mapping.
    """
    def decorator_upsert(func):
        @functools.wraps(func)
        def wrapper_upsert(*args, **kwargs):
            # Execute the main function
            result = func(*args, **kwargs)

            # Retrieve 'self' from args (assuming the first argument is 'self')
            if len(args) == 0:
                raise ValueError("The decorated function must have 'self' as its first argument.")
            self = args[0]

            # Retrieve the 'book' object from the function arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            book = bound_args.arguments.get(obj_arg_name)

            if book is None:
                raise ValueError(f"The function '{func.__name__}' must have an argument named '{obj_arg_name}'.")

            # Retrieve the CSV file path and headers mapping from 'self'
            csv_file_path = getattr(self, csv_file_path_attr, None)
            headers_mapping = getattr(self, headers_mapping_attr, None)

            if csv_file_path is None:
                raise AttributeError(f"The object does not have attribute '{csv_file_path_attr}'.")
            if headers_mapping is None:
                raise AttributeError(f"The object does not have attribute '{headers_mapping_attr}'.")

            # Convert the book object to JSON-like dictionary
            obj_json = book.to_json()

            # Perform the upsert operation
            csv_manager.upsert_obj_to_csv(obj_json, csv_file_path, headers_mapping)

            print(f"Added/Updated book to {csv_file_path}")

            return result

        return wrapper_upsert

    return decorator_upsert
