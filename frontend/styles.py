"""
styles.py

Centralized style definitions for Dash components.

This module provides:

- **Style**: An enumeration of style keys used across the application.
- **STYLES**: A dict mapping each Style key to its CSS-like property dict.

Purpose:
- Ensure consistent styling across all Dash components.
- Prevent typos and improve IDE autocompletion.
- Allow easy updates and maintenance of component styles from one place.

Usage:
    from styles import Style, STYLES
    import dash_core_components as dcc

    dcc.Dropdown(style=STYLES[Style.DROPDOWN])

Future Extensions:
- Add new styles to the `Style` enum and corresponding entries to `STYLES`.
"""

from enum import Enum


class Style(Enum):
    """
    Enumeration of supported UI presentation styles.
    """

    APP_TITLE = "app_title"
    BODY = "body"
    BUTTON = "button"
    CARD = "card"
    DROPDOWN = "dropdown"
    ICON = "icon"
    KPI_CARD = "kpi_card"
    KPI_CARD_BODY = "kpi_card_body"
    TABLE = "table"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"
    TABLE_DATA = "table_data"
    TABLE_CONDITIONAL = "table_conditional"
    TAB = "tab"


STYLES = {

    Style.APP_TITLE: {
        "color": "#2c3e50",
        "fontWeight": "bold"
    },

    Style.BODY: {
        "backgroundColor": "#EBEBEB"
    },

    Style.BUTTON: {
        "borderRadius": "9px",
        "height": "39px",
        "border": "none"
    },

    Style.CARD: {
        "borderRadius": "19px",
        "boxShadow": "0 4px 10px rgba(0,0,0,0.12)",
        "border": "none",
        "backgroundColor": "white",
        "padding": "0",
        "margin": "0"
    },

    Style.DROPDOWN: {
        "borderRadius": "9px",
        "height": "39px"
    },

    Style.ICON: {
        "height": "32px",
        "marginBottom": "10px",
        "draggable": "false",
        "cursor": "pointer"
    },

    Style.KPI_CARD: {
        "borderRadius": "19px",
        "boxShadow": "0 4px 10px rgba(0,0,0,0.12)",
        "border": "none",
        "backgroundColor": "white",
        "padding": "0",
        "margin": "0",
        "textAlign": "center",
        "justifyContent": "center"
    },

    Style.KPI_CARD_BODY: {
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",
        "textAlign": "center",
        "height": "100%"
    },

    Style.TAB: {
        "borderRadius": "9px",
        "border": "none",
        "backgroundColor": "rgba(0,0,0,0)"
    },

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
