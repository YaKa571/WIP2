import dash_bootstrap_components as dbc
from dash import html, dcc

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID, Icons


# Info: Edit grid layout in assets/css/tabs.css


def create_user_content() -> html.Div:
    """
    Creates the main content structure for the user tab of the dashboard.

    Returns
    -------
    html.Div
        A Div element containing the formatted components for the user tab content.
    """
    return html.Div(
        className="tab-content-inner user-tab",
        children=[

            _create_heading(),
            _create_search_bars(),
            _create_top_kpis(),
            _create_middle_kpis(),
            _create_bottom_merchant_diagram()

        ])


def _create_heading() -> html.Div:
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element
            html.H4("User", id=ID.USER_TAB_HEADING),
            comp_factory.create_info_icon(ID.USER_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.USER_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Enter a User ID or",
                    html.Br(),
                    "Card ID to update the",
                    html.Br(),
                    "information for the selected",
                    html.Br(),
                    "user or card"
                ])

        ])


def _create_search_bars() -> html.Div:
    """
    Returns heading with two search bars and an info box.
    """
    return html.Div(
        className="d-flex align-items-center mb-3",
        children=[

            _create_single_search_bar("user-id-search-input", "Search by User ID"),
            _create_single_search_bar("card-id-search-input", "Search by Card ID")

        ])


def _create_single_search_bar(input_id: str, placeholder: str) -> html.Div:
    """
    Returns a single search bar with a magnifier icon.
    """
    return html.Div(
        className="search-wrapper p-2 flex-grow-1 me-2 flex-shrink-1",
        children=[

            html.Img(src=Icons.get_icon(IconID.LENS_SEARCH), className="search-icon"),
            dcc.Input(
                id=input_id,
                type='text',
                placeholder=placeholder,
                className='search-input'
            )

        ])


def _create_top_kpis() -> html.Div:
    """
    Creates a row of four KPI boxes for the selected user or card.
    The values update when a User ID or Card ID is entered.
    """
    return html.Div(
        className="user-kpi-row",
        children=[

            html.Div(id="kpi-user-tx-count", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-sum", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-avg", className="user-kpi-box"),
            html.Div(id="kpi-user-card-count", className="user-kpi-box"),

        ])


def _create_middle_kpis() -> html.Div:
    """
    Creates the centered credit limit box.
    """
    return html.Div(
        className="user-kreditlimit-row",
        children=[

            html.Div(id="user-credit-limit-box", className="user-credit-limit-box")

        ])


def _create_bottom_merchant_diagram() -> html.Div:
    """
    Creates the merchant bar chart (incl. dropdown) for the bottom section.
    """
    return html.Div(
        className="user-bottom-merchant-chart-container",
        children=[

            dcc.Dropdown(
                id="merchant-sort-dropdown",
                value="amount",
                clearable=False,
                style={"width": "240px", "marginBottom": "10px"},
                options=[
                    {"label": "Total Amount", "value": "amount"},
                    {"label": "Transaction Count", "value": "count"},
                ]),

            dcc.Graph(
                id="user-merchant-bar-chart",
                config={"displayModeBar": False},
                style={"height": "340px"},
            )

        ]
        , style={
            "background": "#fff",
            "borderRadius": "16px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "padding": "1.5rem",
            "marginTop": "30px"
        }
    )
