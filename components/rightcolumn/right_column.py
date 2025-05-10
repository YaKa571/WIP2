# components/rightcolumn/right_column.py

import dash_bootstrap_components as dbc
from dash import html

from components.rightcolumn.tabs.tab_cluster import create_cluster_content
from components.rightcolumn.tabs.tab_fraud import create_fraud_content
# importiere Deine fünf Builder
from components.rightcolumn.tabs.tab_home import create_home_content
from components.rightcolumn.tabs.tab_merchant import create_merchant_content
from components.rightcolumn.tabs.tab_user import create_user_content
from frontend.component_ids import ID

# nur Label und ID, Builder ziehen wir unten per Mapping
TABS = [
    ("Home", ID.TAB_HOME.value),
    ("Fraud", ID.TAB_FRAUD.value),
    ("Cluster", ID.TAB_CLUSTER.value),
    ("User", ID.TAB_USER.value),
    ("Merchant", ID.TAB_MERCHANT.value),
]

# Mapping Tab-ID → Builder-Funktion
TAB_BUILDERS = {
    ID.TAB_HOME.value: create_home_content,
    ID.TAB_FRAUD.value: create_fraud_content,
    ID.TAB_CLUSTER.value: create_cluster_content,
    ID.TAB_USER.value: create_user_content,
    ID.TAB_MERCHANT.value: create_merchant_content,
}


def create_tabs():
    buttons = []
    for label, tid in TABS:
        buttons.append(
            dbc.Button(
                label,
                id={"type": "custom-tab", "index": tid},
                n_clicks=0,
                className="custom-tab-button"
            )
        )
    return html.Div(buttons, className="d-flex custom-tab-bar")


def create_right_column():
    tabs = create_tabs()

    # Baue für jeden Tab-Inhalt einen Wrapper mit pattern-ID und Basis-Klasse
    wrappers = []
    for idx, (_, tid) in enumerate(TABS):
        builder = TAB_BUILDERS[tid]
        wrappers.append(
            html.Div(
                builder(),
                id={"type": "tab-content", "index": tid},
                className="tab-item active" if idx == 0 else "tab-item hidden"
            )
        )

    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        tabs,
                        html.Div(
                            wrappers,
                            id="custom-tab-content",
                            className="tab-content-wrapper flex-fill"
                        )
                    ],
                    className="d-flex flex-column p-0"
                ),
                className="card h-100"
            )
        ],
        className="right-column d-flex flex-column"
    )