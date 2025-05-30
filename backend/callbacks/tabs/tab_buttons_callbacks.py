import json

from dash import callback, callback_context
from dash.dependencies import Input, Output, ALL

from frontend.layout.right.right_column import TABS
from frontend.component_ids import ID


@callback(
    Output({"type": "custom-tab", "index": ALL}, "className"),
    Output({"type": "tab-content", "index": ALL}, "className"),
    Input({"type": "custom-tab", "index": ALL}, "n_clicks"),
    Input(ID.ACTIVE_TAB_STORE, "data")
)
def update_tabs(n_clicks_list, active_from_store):
    """
    Updates the classes of tab buttons and tab content based on user interaction.

    This function is a callback that dynamically updates the CSS classes
    associated with custom tabs and their corresponding content wrappers
    depending on which tab button was most recently clicked. The function ensures
    only one tab is active at a time by modifying the active tab's button and content
    wrapper classes, while hiding the inactive ones.

    Parameters
    ----------
    n_clicks_list : list of int or None
        A list where each element corresponds to the click count of a respective tab button,
        which the user interacts with. If a button has not been clicked, its count will
        be None.

    Returns
    -------
    tuple of (list of str, list of str)
        A pair of lists representing updated CSS classes. The first list corresponds to
        the button classes for all tabs, while the second list corresponds to the
        content wrapper classes for all tabs.

    Raises
    ------
    None
    """
    ctx = callback_context

    if ctx.triggered and ID.ACTIVE_TAB_STORE in ctx.triggered[0]["prop_id"]:
        active = active_from_store
    elif not ctx.triggered:
        active = TABS[0][1]
    else:
        triggered = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        active = triggered["index"]

    # Button classes
    btn_classes = [
        "custom-tab-button" + (" active" if tid == active else "")
        for _, tid in TABS
    ]

    # Wrapper classes
    content_classes = [
        "tab-item active" if tid == active else "tab-item hidden"
        for _, tid in TABS
    ]

    return btn_classes, content_classes
