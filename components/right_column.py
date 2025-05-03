import dash_bootstrap_components as dbc
from dash import html

from frontend.component_ids import IDs


def create_tabs():
    return dbc.Tabs(
        [
            dbc.Tab(label="Default", tab_id=IDs.TAB_DEFAULT.value),
            dbc.Tab(label="Fraud Transactions", tab_id=IDs.TAB_FRAUD.value),
            dbc.Tab(label="Cluster", tab_id=IDs.TAB_CLUSTER.value),
            dbc.Tab(label="User", tab_id=IDs.TAB_USER.value),
            dbc.Tab(label="Merchant", tab_id=IDs.TAB_MERCHANT.value),
            dbc.Tab(label="Test", tab_id=IDs.TAB_TEST.value),
        ],
        id=IDs.TABS_BAR.value,
        active_tab=IDs.TAB_DEFAULT.value,  # Setting the default tab
        className="tab"
    )


def create_right_column():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    create_tabs(),
                    className="p-0"
                ),
                className="card"
            )
        ],
        className="right-column"
    )
