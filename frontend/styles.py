from enum import Enum


class Style(Enum):
    """
    Represents an enumeration of different style types used for formatting and rendering purposes.

    The Style class is an enumeration that defines various style options related to tables and their
    components. It is meant to provide a clear and structured way to reference specific formatting
    styles, such as for entire tables, their headers, cells, or data content. This enumeration can
    be used in table rendering or styling logic to ensure uniformity and maintainability.

    Attributes:
        TABLE: A style for the entire table.
        TABLE_CELL: A style for individual table cells.
        TABLE_HEADER: A style for the header section of a table.
        TABLE_DATA: A style for the data portion within a table.
        TABLE_CONDITIONAL: A style used for conditional formatting within a table.
    """

    TABLE = "table"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"
    TABLE_DATA = "table_data"
    TABLE_CONDITIONAL = "table_conditional"


STYLES = {

    Style.TABLE: {
        "overflowX": "auto"
    },

    Style.TABLE_CELL: {
        "padding": "8px",
        "textAlign": "center"
    },

    Style.TABLE_HEADER: {
        "backgroundColor": "#0d6efd",
        "color": "white",
        "fontWeight": "bold"
    },

    Style.TABLE_DATA: {
        "backgroundColor": "#ffffff",
        "border": "1px solid #ddd"
    },

    Style.TABLE_CONDITIONAL: [
        # Odd rows (Index 1, 3, 5 ...)
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#f2f2f2"  # Light gray
        },
        # Even rows (Index 0, 2, 4 ...)
        {
            "if": {"row_index": "even"},
            "backgroundColor": "#ffffff"  # White
        }
    ]

}
