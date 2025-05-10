from backend.data_manager import DataManager
from utils.benchmark import Benchmark

benchmark_startup_time = Benchmark("Dash App Startup")
DataManager.initialize()
dm = DataManager.get_instance()

import dash_bootstrap_components as dbc
from dash import Dash, dcc

import components.factories.component_factory as comp_factory
import components.factories.settings_components_factory as settings_comp_factory
from backend.callbacks.settings_callbacks import *  # noqa: F401
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401
from backend.callbacks.tab_callback import update_tabs  # noqa: F401
from backend.callbacks.tab_cluster_callbacks import update_cluster
from components.leftcolumn.left_column import create_left_column
from components.rightcolumn.right_column import create_right_column
from frontend.component_ids import IDs


def create_app():
    app = Dash(__name__, external_stylesheets=
    [dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"],
    # if there are callback problems, set this to False to use debugger
    suppress_callback_exceptions=True,)

    app.title = "Financial Transactions Dashboard"

    app.layout = html.Div(
        [

            # Stores and Divs needed for the layout to work properly
            dcc.Store(id=IDs.APP_STATE_STORE.value),
            dcc.Store(id=IDs.ANIMATION_STATE_STORE.value),
            html.Div(id="app-init-trigger", style={"display": "none"}),
            html.Div(id="layout-ready-signal", style={"display": "none"}),

            # Row with title and dark mode switch
            html.Div(
                [
                    settings_comp_factory.create_icon_button("bi-gear", IDs.BUTTON_SETTINGS_MENU, "settings-menu"),
                    html.H1("Financial Transactions Dashboard",
                            className="m-0 flex-grow-1 text-center"),
                    settings_comp_factory.create_icon_button("bi-sun-fill", IDs.BUTTON_DARK_MODE_TOGGLE),
                    settings_comp_factory.create_settings_canvas()
                ],
                className="dashboard-header d-flex align-items-center"
            ),

            dbc.Row(
                dbc.Col(
                    [

                        # To have a look at a certain data table, add it here and set visible=True
                        comp_factory.create_data_table(IDs.TABLE_USERS, dm.df_users, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_TRANSACTIONS, dm.df_transactions,
                                                       visible=False),
                        comp_factory.create_data_table(IDs.TABLE_CARDS, dm.df_cards, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_MCC, dm.df_mcc, visible=False),

                    ]
                ),
                className="g-0 flex-shrink-0",
                style={"minSize": 0}
            ),

            # Row with Left and Right Column
            html.Div(
                [
                    create_left_column(),
                    create_right_column()
                ],
                className="dashboard-body"
            ),

            # Tooltips
            comp_factory.create_tooltips()
        ],
        id=IDs.DASHBOARD_CONTAINER.value,
        className="dashboard"
    )

    return app


if __name__ == '__main__':
    # Create and run Dash App
    app = create_app()

    # Print startup time
    benchmark_startup_time.print_time(add_empty_line=True)

    app.run(debug=True)
