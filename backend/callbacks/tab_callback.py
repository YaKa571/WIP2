# backend/callbacks/tab_callback.py

import json

from dash import callback, callback_context
from dash.dependencies import Input, Output, ALL

from components.rightcolumn.right_column import TABS


@callback(
    # Button-Klassen
    Output({"type": "custom-tab", "index": ALL}, "className"),
    # Wrapper-Klassen
    Output({"type": "tab-content", "index": ALL}, "className"),
    Input({"type": "custom-tab", "index": ALL}, "n_clicks"),
)
def update_tabs(n_clicks_list):
    """
    Setzt für den geklickten Tab-Button 'active' und
    für den entsprechenden Content-Wrapper 'tab-item active',
    alle anderen Wrapper auf 'tab-item hidden'.
    """
    ctx = callback_context
    if not ctx.triggered:
        active = TABS[0][1]
    else:
        triggered = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        active = triggered["index"]

    # 1) Button-Klassen
    btn_classes = [
        "custom-tab-button" + (" active" if tid == active else "")
        for _, tid in TABS
    ]

    # 2) Wrapper-Klassen
    content_classes = [
        "tab-item active" if tid == active else "tab-item hidden"
        for _, tid in TABS
    ]

    return btn_classes, content_classes