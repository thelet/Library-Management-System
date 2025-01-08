# logger.py
class Logger:
    def log(self, message: str):
        # For simplicity, we print the log message. This can be extended to write to a file.
        print(f"[LOG]: {message}")
