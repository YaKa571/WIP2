import re
from typing import List, Any

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc

from frontend.component_ids import ID


## SETTINGS ##

def create_map_setting_color_scale() -> html.Div:
    """
    Generates a section of the user interface (UI) for selecting a color scale for a map.

    This function creates a dropdown menu UI component with a list of available color scales
    from the Plotly library. Each color scale is presented with a label (human-readable
    name) and its corresponding value. The dropdown allows a user to select one color
    scale for customizing the map's appearance.

    Returns
    -------
    html.Div
        A Div component containing a dropdown menu for selecting a color scale with
        relevant labels and settings.
    """
    color_options = [{"label": re.sub("_", " ", color).upper(), "value": color}
                     for color in sorted(px.colors.named_colorscales())]

    return html.Div(
        [
            html.Label("Color Scale", className="settings-label"),
            dcc.Dropdown(className="settings-dropdown settings-text-centered",
                         options=color_options,
                         id=ID.SETTING_MAP_COLOR_SCALE.value,
                         placeholder="Select a color scale...",
                         style={"width": "100%"},
                         value="blues",
                         clearable=False
                         ),
        ],
        className="settings-item"
    )


def create_general_setting_position() -> html.Div:
    """
    Generates a general settings position dropdown for UI placement configuration.

    The function creates a dropdown component within a Div element to allow the
    user to select a position for settings placement. The options for the dropdown
    include 'top' and 'bottom', where each value correlates to a string value
    ('top' or 'bottom'). The placeholder guides the user to select a position,
    and the dropdown has a default value set. The element includes associated
    CSS classes for styling.

    Returns:
        html.Div: A Div element containing a labeled dropdown selection for
        setting positions.
    """
    placement_options = [
        {"label": "TOP", "value": "top"},
        {"label": "BOTTOM", "value": "bottom"},
        {"label": "LEFT", "value": "start"},
        {"label": "RIGHT", "value": "end"},
    ]

    return html.Div(
        [
            html.Label("Settings Position", className="settings-label"),
            dcc.Dropdown(className="settings-dropdown settings-text-centered",
                         options=placement_options,
                         id=ID.SETTING_GENERAL_CANVAS_PLACEMENT.value,
                         placeholder="Select a placement...",
                         style={"width": "100%"},
                         value="start",
                         clearable=False
                         ),
        ],
        className="settings-item"
    )


def create_general_setting_toggle_tooltips() -> html.Div:
    """
    Creates a general settings toggle component for tooltips.

    This function generates a tooltip toggle UI element. The toggle is represented as a
    switch allowing users to enable or disable tooltips in the application settings.
    The component includes a descriptive label and a switch UI component with
    default settings.

    Returns:
        html.Div: A Div containing the configuration for showing tooltips with a label
        and a toggle switch control.
    """
    return html.Div(
        [
            html.Label("Show Tooltips", className="settings-label"),
            dbc.Switch(id=ID.SETTING_GENERAL_SHOW_TOOLTIPS.value,
                       value=True,
                       className="settings-switch"
                       )
        ],
        className="settings-item"
    )


## ICON BUTTONS ##

def create_icon_button(icon: str, id: ID, extra_cls: str = None, n_clicks: int = 0) -> dbc.Button:
    """
    Creates a square-shaped icon button with customizable icon, ID, and extra CSS
    classes. The button is styled using Bootstrap and includes an icon specified
    by its class name.

    Parameters:
    icon: str
        The Bootstrap icon class to apply on the button.
    id: IDs
        The ID of the button, required for identifying it uniquely in the
        application.
    extra_cls: str, optional
        Additional CSS classes to apply on the button if provided.

    Returns:
    dbc.Button
        Returns a Bootstrap-styled button with the specified icon, unique ID, and
        optional additional classes.
    """
    return dbc.Button(
        html.I(className="bi " + icon),
        id=id,
        className="square-button" + (" " + extra_cls if extra_cls else ""),
        n_clicks=n_clicks
    )


## SETTINGS CANVAS ##

def create_settings_category(title: str = "Default Title", body_children: List[Any] = None) -> dbc.Col:
    """
    Creates a settings category component using Dash Bootstrap Components (dbc). This function
    generates a column containing a styled card with a header and body. The card header displays
    the title, and the body can contain a customizable list of children elements.

    Args:
        title: A string representing the title of the settings category. Defaults to "Default Title".
        body_children: A list of elements to include within the body of the card. Defaults to None,
        resulting in an empty list.

    Returns:
        A dbc.Col instance representing the column containing the styled card.
    """
    children = body_children or []

    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(title, className="settings-card-header"),
                dbc.CardBody(children, className="settings-card-body"),
            ],
            className="settings-card"
        ),
        className="settings-card-col"
    )


def create_settings_canvas_categories() -> dbc.Row:
    """
    Creates a row of categorized settings for the settings canvas.

    This function generates categories of settings for a settings canvas UI layout.
    Each category contains specific settings elements organized within a
    Row layout.

    Returns
    -------
    dbc.Row
        A row containing the settings categories and their respective settings
        elements.
    """
    return dbc.Row(
        [
            create_settings_category("Map Settings", [create_map_setting_color_scale()]),
            create_settings_category("General Settings",
                                     [create_general_setting_position(),
                                      create_general_setting_toggle_tooltips()]),
            create_settings_category("Other Settings",
                                     [html.Div(children=html.Label("Another setting",
                                                                   className="settings-label"),
                                               className="settings-item")])
        ],
        className="settings-cards-row"
    )


def create_settings_canvas():
    """
    Creates and returns a Dash Bootstrap Components Offcanvas component
    configured as the settings canvas.

    This function generates a settings canvas that is initially closed and is
    positioned at the bottom of the interface. The canvas consists of settings
    categories created by the `create_settings_canvas_categories` function.

    Returns:
        Offcanvas: A Dash Bootstrap Components Offcanvas instance configured
        for the settings section.
    """
    return dbc.Offcanvas(
        create_settings_canvas_categories(),
        id=ID.SETTINGS_CANVAS.value,
        title="Settings",
        is_open=False,
        placement="start",
        className="settings-canvas"
    )
