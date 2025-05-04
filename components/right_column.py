import dash_bootstrap_components as dbc
from dash import html

from frontend.component_ids import IDs

TABS = [
    ("Default", IDs.TAB_DEFAULT.value),
    ("Fraud", IDs.TAB_FRAUD.value),
    ("Cluster", IDs.TAB_CLUSTER.value),
    ("User", IDs.TAB_USER.value),
    ("Merchant", IDs.TAB_MERCHANT.value),
]

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

    return html.Div(
        buttons,
        className="d-flex custom-tab-bar"
    )


def create_right_column():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        create_tabs(),
                        html.Div(id="custom-tab-content", className="tab-content-wrapper flex-fill")
                    ],
                    className="d-flex flex-column p-0"
                ),
                className="card h-100"
            )
        ],
        className="right-column"
    )
