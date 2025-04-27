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
    TABLE = "table"
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

    Style.TABLE: {
        "overflowX": "auto"
    },

    Style.TAB: {
        "borderRadius": "9px",
        "border": "none",
        "backgroundColor": "rgba(0,0,0,0)"
    },

}
