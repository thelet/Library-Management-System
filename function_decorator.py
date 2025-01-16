from functools import wraps
from exceptions import PermissionDeniedException


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