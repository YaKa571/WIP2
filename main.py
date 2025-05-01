from utils.benchmark import Benchmark

benchmark_startup_time = Benchmark("Dash App Startup")

import dash_bootstrap_components as dbc
from dash import Dash, html

import components.component_factory as comp_factory
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401 (don't remove this comment!)
from backend.data_manager import DataManager
from components.left_column import create_left_column
from components.right_column import create_right_column
from frontend.component_ids import IDs
from frontend.styles import STYLES, Style


def create_app(data_manager: DataManager):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "Financial Transactions Dashboard"

    app.layout = dbc.Container(
        [
            # Row with Title
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(
                            "Financial Transactions Dashboard",
                            className="text-center m-0 pb-3",
                            style=STYLES[Style.APP_TITLE]
                        ),

                        # To have a look at a certain data table, add it here and set visible=True
                        comp_factory.create_data_table(IDs.TABLE_USERS, data_manager.df_users, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_TRANSACTIONS, data_manager.df_transactions,
                                                       visible=False),
                        comp_factory.create_data_table(IDs.TABLE_CARDS, data_manager.df_cards, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_MCC, data_manager.df_mcc, visible=False),

                    ]
                ),
                className="g-0 flex-shrink-0"
            ),

            # Row with Left and Right Column
            dbc.Row(
                [
                    create_left_column(data_manager),
                    create_right_column()
                ],
                className="gx-3 flex-grow-1",
                style={"minHeight": "0"}
            )
        ],
        fluid=True,
        className="p-3 m-0 d-flex flex-column",
        style=STYLES[Style.BODY]
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
