import os

class Logger:
    def __init__(self):
        # Define the log file path
        self.log_file = os.path.join(os.getcwd(), "log.txt")

        # Ensure the log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as file:
                file.write("Log File Created\n")
        # Initial log entry

    def log(self, message: str, print_to_console: bool = True):
        # Format the log message
        formatted_message = f"[LOG]: {message}"

        # Write the log message to the file
        try:
            with open(self.log_file, "a") as file:
                file.write(formatted_message + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")

        if print_to_console:
            print(formatted_message)

