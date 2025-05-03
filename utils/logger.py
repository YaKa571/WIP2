def log(message: str, level=0):
    """
    Logs a message to the console with optional indentation based on level.

    The function prints the given message to the console, with an indentation
    level controlled by the 'level' parameter.

    Args:
        message (str): The message to be logged.
        level (int, optional): The indentation level for the message. Defaults to 0.
    """
    indent = "  " * level
    print(f"{indent}{message}")
