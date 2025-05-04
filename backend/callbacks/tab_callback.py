import json

from dash import callback, Output, Input, callback_context, html, ALL

from components.right_column import TABS
from frontend.component_ids import IDs


@callback(
    # Update className of all buttons
    Output({"type": "custom-tab", "index": ALL}, "className"),
    # Update the content area
    Output("custom-tab-content", "children"),
    Input({"type": "custom-tab", "index": ALL}, "n_clicks"),
)
def update_tabs(n_clicks_list):
    # Determine which button was clicked last
    ctx = callback_context
    if not ctx.triggered:
        # No click: Default-Tab
        active = TABS[0][1]
    else:
        # prop_id looks like this: '{"type":"custom-tab","index":"Fraud"}.n_clicks'
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        active = json.loads(triggered_id)["index"]

    # Generate classNames: add "active" only for the active tab
    classnames = []
    for _, tid in TABS:
        cls = "custom-tab-button"
        if tid == active:
            cls += " active"
        classnames.append(cls)

    # Render content based on active ID
    # TODO: Set content from components_factory later on
    if active == IDs.TAB_FRAUD.value:
        content = (html.H3("Fraud content", className="card-title text-center"),
                   html.Div(className="tab-content-wrapper flex-fill"))
    elif active == IDs.TAB_CLUSTER.value:
        content = (html.H3("Cluster content", className="card-title text-center"),
                   html.Div(className="tab-content-wrapper flex-fill"))
    elif active == IDs.TAB_USER.value:
        content = (html.H3("User content", className="card-title text-center"),
                   html.Div(className="tab-content-wrapper flex-fill"))
    elif active == IDs.TAB_MERCHANT.value:
        content = (html.H3("Merchant content", className="card-title text-center"),
                   html.Div(className="tab-content-wrapper flex-fill"))
    else:
        content = (html.H3("Default content", className="card-title text-center"),
                   html.Div(className="tab-content-wrapper flex-fill"))

    return classnames, content
