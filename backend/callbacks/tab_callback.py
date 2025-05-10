import json

from dash import callback, Output, Input, callback_context
from dash.dependencies import ALL

from components.rightcolumn.right_column import TABS
from components.rightcolumn.tabs.tab_cluster import create_cluster_content
from components.rightcolumn.tabs.tab_fraud import create_fraud_content
from components.rightcolumn.tabs.tab_home import create_home_content
from components.rightcolumn.tabs.tab_merchant import create_merchant_content
from components.rightcolumn.tabs.tab_user import create_user_content
from frontend.component_ids import IDs

# Mapping tabs to their content‐builder functions
TAB_CONTENT_BUILDERS = {
    IDs.TAB_HOME.value: create_home_content,
    IDs.TAB_FRAUD.value: create_fraud_content,
    IDs.TAB_CLUSTER.value: create_cluster_content,
    IDs.TAB_USER.value: create_user_content,
    IDs.TAB_MERCHANT.value: create_merchant_content,
}


@callback(
    Output({"type": "custom-tab", "index": ALL}, "className"),
    Output("custom-tab-content", "children"),
    Input({"type": "custom-tab", "index": ALL}, "n_clicks"),
)
def update_tabs(n_clicks_list):
    """
    Handles updating the className of custom tabs and determining the content
    to render based on the active tab selected by users.

    The function listens for user interactions (click events) on custom tabs
    and updates their className to reflect the active state. Simultaneously,
    it determines and updates the content displayed in the custom tab content
    area using the appropriate content builder function.

    @param n_clicks_list: List representing the number of clicks for each tab.
                          Monitors click events for tabs.
    @type n_clicks_list: List[int] | None

    @return: A tuple containing a list of className updates for custom tabs
             and the content for the active tab area.
    @rtype: Tuple[List[str], Any]
    """
    ctx = callback_context

    # Determine active tab index from triggered event
    if not ctx.triggered:
        # no click yet -> default to first tab
        active = TABS[0][1]
    else:
        # prop_id looks like '{"type":"custom-tab","index":"Fraud"}.n_clicks'
        triggered_str = ctx.triggered[0]["prop_id"].split(".")[0]
        triggered_id = json.loads(triggered_str)
        active = triggered_id["index"]

    # Build className list, adding "active" to the selected tab
    classnames = [
        "custom-tab-button" + (" active" if tid == active else "")
        for _, tid in TABS
    ]

    # Select the right builder, fallback to Home
    builder = TAB_CONTENT_BUILDERS.get(active, create_home_content)
    content = builder()

    return classnames, content
