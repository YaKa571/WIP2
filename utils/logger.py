# Constants
INDENT_CHARS = "  "
DEBUG_START_MARKER = "⛔ "
DEBUG_END_MARKER = " ⛔"


def _get_debug_markers(debug: bool) -> tuple[str, str]:
    """Returns debug start and end markers if debug is enabled."""
    if debug:
        return DEBUG_START_MARKER, DEBUG_END_MARKER
    return "", ""


def log(message: str, indent_level: int = 0, debug: bool = False) -> None:
    """
    Logs a message with optional indentation and debug markers.

    Prints a given message to the console, optionally prefixed with an indentation
    level and debug markers. The level of indentation is determined by the
    `indent_level` parameter, which multiplies two spaces for every level.
    If `debug` is enabled, special markers are added to the start and end of
    the message.

    Parameters:
        message: str
            The message to be logged.
        indent_level: int, optional
            The level of indentation for the message. Defaults to 0.
        debug: bool, optional
            A flag indicating if debug markers should be added to the message.
            Defaults to False.
    """
    indent_level = 1 if debug else indent_level
    indent = INDENT_CHARS * indent_level
    debug_start, debug_end = _get_debug_markers(debug)
    print(f"{indent}{debug_start}{message}{debug_end}")
