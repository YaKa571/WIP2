import dash_bootstrap_components as dbc

from pyFiles.frontend.component_ids import IDs
from pyFiles.frontend.styles import STYLES, Style


def create_tabs():
    return dbc.Tabs(
        [
            dbc.Tab(label="Default", tab_id=IDs.TAB_DEFAULT.value),
            dbc.Tab(label="Fraud Transactions", tab_id=IDs.TAB_FRAUD.value),
            dbc.Tab(label="Cluster", tab_id=IDs.TAB_CLUSTER.value),
            dbc.Tab(label="User", tab_id=IDs.TAB_USER.value),
            dbc.Tab(label="Merchant", tab_id=IDs.TAB_MERCHANT.value),
        ],
        id=IDs.TABS_BAR.value,
        active_tab=IDs.TAB_DEFAULT.value,  # Setting the default tab
        style=STYLES[Style.TAB]
    )


def create_right_column():
    return dbc.Col(
        [
            dbc.Card(
                dbc.CardBody(create_tabs()),
                style=STYLES[Style.CARD],
                className="flex-fill"
            )
        ],
        width=6,
        className="d-flex flex-column"
    )
