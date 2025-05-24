from backend.data_setup.tabs import tab_cluster_data_setup
from dash import dcc, html
tab_cluster_data_setup.get_cluster_merchant_group_dropdown()
from frontend.component_ids import ID



def get_cluster_merchant_group_input_container():
    my_merchant_groups = tab_cluster_data_setup.get_cluster_merchant_group_dropdown()
    options = [{'label': group, 'value': group} for group in my_merchant_groups]

    default_value = my_merchant_groups[0] if my_merchant_groups else None

    return html.Div([
        html.Label("Select Merchant Group:", className="dropdown-label"),
        dcc.Dropdown(
            id=ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN,
            options=options,
            value=default_value,
            placeholder="Choose a merchant group...",
            searchable=True,
            multi=False,
            style={"width": "100%"}
        )
    ],
        className="dropdown-container"
    )