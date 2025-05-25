from dash import Input, Output, callback, html
from dash import dcc


@callback(
    Output("fraud-sub-tab-content", "children"),
    Input("fraud-sub-tabs", "value")
)
def update_fraud_subtabs(selected_tab: str):
    if selected_tab == "map":
        return html.Div([
            html.H5("🗺️ This is the Map View (Dummy)"),
            dcc.Graph(id="fraud-map")  # Already filled from another callback
        ])
    elif selected_tab == "table":
        return html.Div([
            html.H5("📊 This is the Table View (Dummy)"),
            html.Div(id="fraud-table-wrapper")  # Already exists, will be filled
        ])
    else:
        return html.Div("⚠️ Unknown Tab selected")
