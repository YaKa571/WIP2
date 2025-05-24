from backend.data_manager import DataManager
from utils import logger
from utils.benchmark import Benchmark

logger.log("\nℹ️ Starting Dash App...")
benchmark_startup_time = Benchmark("Dash App Startup")
DataManager.initialize()
dm: DataManager = DataManager.get_instance()

import dash_bootstrap_components as dbc
from dash import Dash, dcc

import components.factories.component_factory as comp_factory
import components.factories.settings_components_factory as settings_comp_factory

from backend.callbacks.settings_callbacks import *  # noqa: F401
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401
from backend.callbacks.tabs.tab_buttons_callbacks import update_tabs  # noqa: F401
from backend.callbacks.tabs.tab_cluster_callbacks import update_cluster  # noqa: F401
from backend.callbacks.tabs.tab_user_callbacks import (update_user_kpis, update_credit_limit,  # noqa: F401
                                                       update_merchant_bar_chart)  # noqa: F401
from backend.callbacks.tabs.tab_home_callbacks import (store_selected_state, update_all_pies,  # noqa: F401
                                                       update_bar_chart, bridge_home_to_user_tab)  # noqa: F401
from backend.callbacks.tabs.tab_merchant_callbacks import update_merchant  # noqa: F401

from components.leftcolumn.left_column import create_left_column
from components.rightcolumn.right_column import create_right_column
from frontend.component_ids import ID


def create_app():
    app = Dash(__name__, external_stylesheets=
    [dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"],
               # If there are callback problems, set this False to use debugger
               suppress_callback_exceptions=True)

    app.title = "Financial Transactions Dashboard"

    app.layout = html.Div(
        className="dashboard",
        id=ID.DASHBOARD_CONTAINER.value,
        children=[

            # Stores and Divs needed for the layout to work properly
            dcc.Store(id=ID.APP_STATE_STORE.value),
            dcc.Store(id=ID.ANIMATION_STATE_STORE.value),
            dcc.Store(id=ID.HOME_TAB_SELECTED_STATE_STORE, data=None),
            dcc.Store(id=ID.ACTIVE_TAB_STORE, data=ID.TAB_HOME),
            html.Div(id="app-init-trigger", style={"display": "none"}),
            html.Div(id="layout-ready-signal", style={"display": "none"}),

            # Row with title and dark mode switch
            html.Div(
                className="dashboard-header d-flex align-items-center",
                children=[

                    settings_comp_factory.create_icon_button("bi-gear", ID.BUTTON_SETTINGS_MENU, "settings-menu"),
                    html.H1("Financial Transactions Dashboard", className="m-0 flex-grow-1 text-center"),
                    settings_comp_factory.create_icon_button("bi-sun-fill", ID.BUTTON_DARK_MODE_TOGGLE),
                    settings_comp_factory.create_settings_canvas()

                ]),

            dbc.Row(
                className="g-0 flex-shrink-0",
                style={"minSize": 0},
                children=[

                    dbc.Col(
                        children=[

                            # To have a look at a certain data table, add it here and set visible=True
                            comp_factory.create_data_table(ID.TABLE_USERS, dm.df_users, visible=False),
                            comp_factory.create_data_table(ID.TABLE_TRANSACTIONS, dm.df_transactions, visible=False),
                            comp_factory.create_data_table(ID.TABLE_CARDS, dm.df_cards, visible=False),
                            comp_factory.create_data_table(ID.TABLE_MCC, dm.df_mcc, visible=False),

                        ])
                ]),

            # Row with Left and Right Column
            html.Div(
                className="dashboard-body",
                children=[

                    create_left_column(),
                    create_right_column()

                ]),

            # Tooltips
            comp_factory.create_tooltips()
        ])

    return app


if __name__ == '__main__':
    # Create and run Dash App
    app = create_app()

    # Print startup time
    benchmark_startup_time.print_time(add_empty_line=True, level=0)

    app.run(debug=True)
