import dash_bootstrap_components as dbc
from dash import html, dcc

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from backend.data_manager import DataManager

dm: DataManager = DataManager.get_instance()


def create_fraud_content():
    amount = "50,000"
    fraudSum = "$2,168,783.77"
    avg = "$43.38"

    return html.Div(
        className="tab-content-inner fraud-tab",
        children=[

            # 💬 Heading mit Tooltip
            _create_heading(),

            # 🔢 Kennzahlen Karte
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Amount of Transactions", className="card-title"),
                        html.H2(amount, className="card-text", id="fraud-trans-count")
                    ])
                ])),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Sum Value", className="card-title"),
                        html.H2(fraudSum, className="card-text", id="fraud-sum-value")
                    ])
                ])),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Average Amount per Transaction", className="card-title"),
                        html.H2(avg, className="card-text", id="fraud-avg-value")
                    ])
                ])),
            ], className="mb-4"),

            # 🗺️ Karte mit Fraud-Daten (noch Dummy)
            html.Div([
                html.H5("Map: Fraud Transactions – Amount / Value"),
                dcc.Graph(id="fraud-map")
            ], className="mb-5"),

            # 📊 Tabelle mit Dummy Fraud-Fällen
            html.Div([
                html.H5("Table of Suspicious Transactions (Dummy)", className="mt-4"),
                html.Div(
                    id="fraud-table-wrapper",
                    children=[
                        dbc.Spinner(dbc.Table(id="fraud-table", bordered=True, hover=True, responsive=True, striped=True))
                    ]
                )
            ], className="mb-5"),

            # 🔎 Detailbereich für User Fokus (dummy)
            html.Div(
                id="fraud-detail-panel",
                className="alert alert-info mt-4",
                children="ℹ️ Click on a transaction to see details here."
            ),

            # 🧭 Sub Tabs mit Dummy-Inhalten
            html.Div([
                dcc.Tabs(
                    id="fraud-sub-tabs",
                    value="map",
                    children=[
                        dcc.Tab(label="Map View", value="map"),
                        dcc.Tab(label="Table View", value="table"),
                    ],
                ),
                html.Div(id="fraud-sub-tab-content")
            ], className="mb-5"),
        ]
    )


def _create_heading() -> html.Div:
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            html.P(),  # Dummy element
            html.H4("Fraud", id=ID.FRAUD_TAB_HEADING),
            comp_factory.create_info_icon(ID.FRAUD_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.FRAUD_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Placeholder for",
                    html.Br(),
                    "the tooltip",
                    html.Br(),
                    "..."
                ]
            )
        ]
    )
