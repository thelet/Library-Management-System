from functools import wraps
from design_patterns.exceptions import PermissionDeniedException
import functools
import inspect
from manage_files import csv_manager
# design_patterns/function_decorator.py

from typing import Callable, Any, List, Dict
from functools import wraps
from manage_files.csv_manager import update_csv

def permission_required(permission: str):
    """
    A decorator to check if the caller has the required permission before executing the function.

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



def update_csv_after(upsert_configs: List[Dict[str, str]]):
    """
    Decorator to perform multiple CSV upsert operations after the wrapped function executes.

    :param upsert_configs: List of dictionaries with keys:
                           - 'obj_arg_name': Name of the function argument that holds the object to upsert.
                           - 'csv_file_path_attr': Attribute name in 'self' that holds the CSV file path.
                           - 'headers_mapping_attr': Attribute name in 'self' that holds the headers mapping.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the wrapped function
            result = func(*args, **kwargs)

            # Assume 'self' is the first positional argument
            if not args:
                print("Decorator Error: 'self' is expected as the first positional argument.")
                return result

            self_obj = args[0]

            # Prepare the list of upsert arguments
            args_list = []
            for config in upsert_configs:
                obj_arg_name = config.get("obj_arg_name")
                csv_file_path_attr = config.get("csv_file_path_attr")
                headers_mapping_attr = config.get("headers_mapping_attr")

                # Extract the object to upsert from kwargs or args
                obj = kwargs.get(obj_arg_name)
                if not obj:
                    # Attempt to get from positional args (assuming object is after 'self')
                    obj_index = list(func.__code__.co_varnames).index(obj_arg_name)
                    if obj_index < len(args):
                        obj = args[obj_index]

                if not obj:
                    print(f"Decorator Warning: Object '{obj_arg_name}' not found in function arguments.")
                    continue  # Skip this upsert operation

                # Extract CSV file path and headers mapping from 'self'
                csv_file_path = getattr(self_obj, csv_file_path_attr, None)
                headers_mapping = getattr(self_obj, headers_mapping_attr, None)

                if not csv_file_path or not headers_mapping:
                    print(
                        f"Decorator Warning: Attributes '{csv_file_path_attr}' or '{headers_mapping_attr}' not found in 'self'.")
                    continue  # Skip this upsert operation

                # Prepare the upsert argument dictionary
                upsert_args = {
                    "obj_data": obj.to_json(),
                    "csv_file_path": csv_file_path,
                    "headers_mapping": headers_mapping
                }
                args_list.append(upsert_args)

            # Perform the CSV updates if there are any upsert operations
            if args_list:
                try:
                    update_csv(args_list)
                except ValueError as ve:
                    print(f"Decorator Error: {ve}")
                except Exception as e:
                    print(f"Decorator Unexpected Error: {e}")

            return result

        return wrapper

    return decorator

