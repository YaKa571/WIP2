from backend.data_manager import DataManager
from utils import logger
from utils.benchmark import Benchmark

logger.log("\nℹ️ Starting Dash App...")
benchmark_startup_time = Benchmark("Dash App Startup")
DataManager.initialize()
dm: DataManager = DataManager.get_instance()

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
import components.constants as const

import components.factories.component_factory as comp_factory
import components.factories.settings_components_factory as settings_comp_factory

from backend.callbacks.settings_callbacks import (  # noqa: F401
    toggle_settings_canvas, update_app_state, prepare_map_update,
    render_map, initialize_layout, trigger_initial_render,
    toggle_tooltips, change_settings_position, initialize_settings_components
)
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401
from backend.callbacks.tabs.tab_buttons_callbacks import update_tabs  # noqa: F401
from backend.callbacks.tabs.tab_cluster_callbacks import (  # noqa: F401
    update_cluster, set_cluster_tab, toggle_legend
)
from backend.callbacks.tabs.tab_user_callbacks import (  # noqa: F401
    update_user_kpis, update_credit_limit,
    update_merchant_bar_chart,
    bridge_user_to_merchant_tab,
    toggle_inputs, update_tab_heading
)
from backend.callbacks.tabs.tab_home_callbacks import (  # noqa: F401
    store_selected_state, update_all_pies,
    update_bar_chart, bridge_home_to_user_tab
)
from backend.callbacks.tabs.tab_merchant_callbacks import (  # noqa: F401
    update_merchant, set_merchant_tab
)
from backend.callbacks.tabs.tab_fraud_callbacks import (  # noqa: F401
    update_total_fraud_cases, update_total_transactions,
    update_fraud_ratio, update_fraud_by_state,
    update_fraud_by_age
)

from frontend.layout.left.left_column import create_left_column
from frontend.layout.right.right_column import create_right_column
from frontend.component_ids import ID


def create_app(suppress_callback_exceptions: bool = True, add_data_tables: bool = False) -> Dash:
    """
    Creates and configures a Dash application instance for the Financial Transactions Dashboard.

    This function sets up the application with a specified layout, initializes necessary
    data stores, and adds interface components such as tables, headers, columns, and tooltips.
    It is designed to use Dash's `dbc.themes.BOOTSTRAP` stylesheet and an external
    Bootstrap Icons stylesheet for styling.

    Parameters:
        suppress_callback_exceptions: bool
            Indicates whether callback exceptions are suppressed. When set to `False`,
            the Dash debugger will handle callback-related issues. Defaults to `True`.
        add_data_tables: bool
            Whether to add data tables to the layout. Defaults to `False`.

    Returns:
        Dash
            A Dash application instance configured for the Financial Transactions Dashboard.
    """
    dash_app = Dash(
        __name__,
        suppress_callback_exceptions=suppress_callback_exceptions,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
            "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;"
            "1,300;1,400;1,700;1,900&family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
        ]
    )

    dash_app.title = "Financial Transactions Dashboard"

    dash_app.layout = html.Div(
        className="dashboard dark-mode",
        id=ID.DASHBOARD_CONTAINER,
        children=[

            # Stores and Divs needed for the layout to work properly
            dcc.Store(id=ID.APP_STATE_STORE, data=const.APP_STATE_STORE_DEFAULT, storage_type="session"),
            dcc.Store(id=ID.ANIMATION_STATE_STORE),
            dcc.Store(id=ID.HOME_TAB_SELECTED_STATE_STORE, data=None),
            dcc.Store(id=ID.ACTIVE_TAB_STORE, data=ID.TAB_HOME, storage_type="session"),
            dcc.Store(id=ID.MERCHANT_SELECTED_BUTTON_STORE, data="all"),
            dcc.Store(id=ID.CLUSTER_SELECTED_BUTTON_STORE, data={"main": "total_value", "age": "all_ages"}),
            html.Div(id="app-init-trigger", style={"display": "none"}),
            html.Div(id="layout-ready-signal", style={"display": "none"}),

            # Row with title and dark mode switch
            html.Div(
                className="dashboard-header d-flex align-items-center",
                children=[

                    settings_comp_factory.create_icon_button("bi-gear", ID.BUTTON_SETTINGS_MENU, "settings-menu"),
                    html.H1("Financial Transactions Dashboard", className="m-0 flex-grow-1 text-center"),
                    settings_comp_factory.create_icon_button("bi-sun-fill", ID.BUTTON_DARK_MODE_TOGGLE,
                                                             n_clicks=1 if const.DEFAULT_DARK_MODE else 0),
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
                ]) if add_data_tables else None,

            # Row with Left and Right Column
            html.Div(
                className="dashboard-body",
                children=[

                    create_left_column(),
                    html.Div(className="resize-handle"),
                    create_right_column()

                ]),

            # Tooltips
            comp_factory.create_tooltips()
        ])

    return dash_app


if __name__ == '__main__':
    # Create and run Dash App
    app = create_app()

    # Print startup time
    benchmark_startup_time.print_time(add_empty_line=True, level=0)

    app.run(debug=False)
