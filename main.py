from backend.data_manager import DataManager
from utils.benchmark import Benchmark

benchmark_startup_time = Benchmark("Dash App Startup")
DataManager.initialize()
dm: DataManager = DataManager.get_instance()

import dash_bootstrap_components as dbc
from dash import Dash, dcc

import components.factories.component_factory as comp_factory
import components.factories.settings_components_factory as settings_comp_factory

from backend.callbacks.settings_callbacks import *  # noqa: F401
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401
from backend.callbacks.tab_callback import update_tabs  # noqa: F401
from backend.callbacks.tab_cluster_callbacks import update_cluster  # noqa: F401
from backend.callbacks.user_kpi_callbacks import *  # noqa: F401

from components.leftcolumn.left_column import create_left_column
from components.rightcolumn.right_column import create_right_column
from frontend.component_ids import ID


def create_app():
    app = Dash(__name__, external_stylesheets=
    [dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"],
               # If there are callback problems, set this False to use debugger
               suppress_callback_exceptions=False)

    app.title = "Financial Transactions Dashboard"

    app.layout = html.Div(children=[

        # Stores and Divs needed for the layout to work properly
        dcc.Store(id=ID.APP_STATE_STORE.value),
        dcc.Store(id=ID.ANIMATION_STATE_STORE.value),
        html.Div(id="app-init-trigger", style={"display": "none"}),
        html.Div(id="layout-ready-signal", style={"display": "none"}),

        # Row with title and dark mode switch
        html.Div(children=[

            settings_comp_factory.create_icon_button("bi-gear", ID.BUTTON_SETTINGS_MENU, "settings-menu"),
            html.H1("Financial Transactions Dashboard", className="m-0 flex-grow-1 text-center"),
            settings_comp_factory.create_icon_button("bi-sun-fill", ID.BUTTON_DARK_MODE_TOGGLE),
            settings_comp_factory.create_settings_canvas()

        ],
            className="dashboard-header d-flex align-items-center"
        ),

        dbc.Row(
            dbc.Col(children=[

                # To have a look at a certain data table, add it here and set visible=True
                comp_factory.create_data_table(ID.TABLE_USERS, dm.df_users, visible=False),
                comp_factory.create_data_table(ID.TABLE_TRANSACTIONS, dm.df_transactions, visible=False),
                comp_factory.create_data_table(ID.TABLE_CARDS, dm.df_cards, visible=False),
                comp_factory.create_data_table(ID.TABLE_MCC, dm.df_mcc, visible=False),

            ]
            ),
            className="g-0 flex-shrink-0",
            style={"minSize": 0}
        ),

        # Row with Left and Right Column
        html.Div(children=[

            create_left_column(),
            create_right_column()

        ],
            className="dashboard-body"
        ),

        # Tooltips
        comp_factory.create_tooltips()
    ],
        id=ID.DASHBOARD_CONTAINER.value,
        className="dashboard"
    )

    return app


if __name__ == '__main__':
    # Create and run Dash App
    app = create_app()

    # Print startup time
    benchmark_startup_time.print_time(add_empty_line=True)

    app.run(debug=True)
