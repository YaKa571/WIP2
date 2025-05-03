from utils.benchmark import Benchmark

benchmark_startup_time = Benchmark("Dash App Startup")

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

import components.component_factory as comp_factory
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401 (don't remove this comment!)
from backend.callbacks.darkmode_callback import toggle_dark_mode  # noqa: F401
from backend.data_manager import DataManager
from components.left_column import create_left_column
from components.right_column import create_right_column
from frontend.component_ids import IDs


def create_app(data_manager: DataManager):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                               "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"])
    app.title = "Financial Transactions Dashboard"

    app.layout = html.Div(
        [

            # Store to persist the dark-mode state
            dcc.Store(id=IDs.DARK_MODE_STORE.value, data=False),

            # Row with title and dark mode switch
            html.Div(
                [
                    html.H1("Financial Transactions Dashboard",
                            className="m-0 flex-grow-1 text-center"),
                    dbc.Button(
                        html.I(className="bi bi-sun-fill"),
                        id=IDs.DARK_MODE_TOGGLE.value,
                        className="ms-auto btn-mode-toggle",
                        n_clicks=0
                    )
                ],
                className="dashboard-header d-flex align-items-center"
            ),

            dbc.Row(
                dbc.Col(
                    [

                        # To have a look at a certain data table, add it here and set visible=True
                        comp_factory.create_data_table(IDs.TABLE_USERS, data_manager.df_users, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_TRANSACTIONS, data_manager.df_transactions,
                                                       visible=False),
                        comp_factory.create_data_table(IDs.TABLE_CARDS, data_manager.df_cards, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_MCC, data_manager.df_mcc, visible=False),

                    ]
                ),
                className="g-0 flex-shrink-0",
                style={"minSize": 0}
            ),

            # Row with Left and Right Column
            html.Div(
                [
                    create_left_column(data_manager),
                    create_right_column()
                ],
                className="dashboard-body"
            )
        ],
        id=IDs.DASHBOARD_CONTAINER.value,
        className="dashboard dark-mode"
    )

    return app


if __name__ == '__main__':
    # Initialize DataManager
    dm = DataManager()

    # Create and run Dash App
    app = create_app(dm)

    # Print startup time
    benchmark_startup_time.print_time(add_empty_line=True)

    app.run(debug=True)
