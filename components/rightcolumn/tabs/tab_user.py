import dash_bootstrap_components as dbc
from dash import html, dcc

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID, Icons


def create_user_content() -> html.Div:
    """
    Creates the main content structure for the user tab of the dashboard.

    Returns
    -------
    html.Div
        A Div element containing the formatted components for the user tab content.
    """
    return html.Div(
        children=[
            _create_user_heading(),
            _create_top_kpis(),
            _create_middle_kpis(),
            _create_bottom_merchant_diagram()
        ],
        className="tab-content-inner"
    )


def _create_user_heading() -> html.Div:
    """
    Returns heading with two search bars and an info box.
    """
    return html.Div(
        children=[
            _create_single_search_bar("user-id-search-input", "Search by User ID"),
            _create_single_search_bar("card-id-search-input", "Search by Card ID"),
            _create_info_icon_with_tooltip()
        ],
        className="d-flex align-items-center mb-4"
    )


def _create_single_search_bar(input_id: str, placeholder: str) -> html.Div:
    """
    Returns a single search bar with a magnifier icon.
    """
    return html.Div(
        [
            html.Img(src=Icons.get_icon(IconID.LENS_SEARCH), className="search-icon"),
            dcc.Input(
                id=input_id,
                type='text',
                placeholder=placeholder,
                className='search-input',
            )
        ],
        className="search-wrapper p-2 flex-grow-1 me-2"
    )


def _create_info_icon_with_tooltip() -> html.Div:
    """
    Returns an info icon with a tooltip explaining the usage.
    """
    return html.Div(children=[

        comp_factory.create_info_icon(ID.USER_TAB_INFO_ICON),
        dbc.Tooltip(
            "Enter a User ID or Card ID to update the information for the selected user or card.",
            target="user-tab-info-icon",
            placement="bottom",
            className="user-info-tooltip"
        )

    ]
    )


def _create_top_kpis() -> html.Div:
    """
    Creates a row of four KPI boxes for the selected user or card.
    The values update when a User ID or Card ID is entered.
    """
    return html.Div(
        [
            html.Div(id="kpi-user-tx-count", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-sum", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-avg", className="user-kpi-box"),
            html.Div(id="kpi-user-card-count", className="user-kpi-box"),
        ],
        className="user-kpi-row"
    )


def _create_middle_kpis() -> html.Div:
    """
    Creates the centered credit limit box.
    """
    return html.Div(
        children=[
            html.Div(id="user-credit-limit-box", className="user-credit-limit-box")
        ],
        className="user-kreditlimit-row"
    )


def _create_bottom_merchant_diagram() -> html.Div:
    """
    Creates the merchant bar chart (incl. dropdown) for the bottom section.
    """
    return html.Div(
        children=[
            dcc.Dropdown(
                id="merchant-sort-dropdown",
                options=[
                    {"label": "Total Amount", "value": "amount"},
                    {"label": "Transaction Count", "value": "count"},
                ],
                value="amount",
                clearable=False,
                style={"width": "240px", "marginBottom": "10px"},
            ),
            dcc.Graph(
                id="user-merchant-bar-chart",
                config={"displayModeBar": False},
                style={"height": "340px"},
            )
        ],
        className="user-bottom-merchant-chart-container",
        style={
            "background": "#fff",
            "borderRadius": "16px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "padding": "1.5rem",
            "marginTop": "30px"
        }
    )
