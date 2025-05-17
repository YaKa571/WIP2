from dash import html, dcc
from frontend.icon_manager import IconID, Icons
import dash_bootstrap_components as dbc
from backend.data_manager import DataManager

dm: DataManager = DataManager.get_instance()

def create_user_content() -> html.Div:
    return html.Div(
        [
            _create_user_heading(),
            html.Div(  # ROW der vier KPIs
                [
                    html.Div(id="kpi-user-tx-count", className="user-kpi-box"),
                    html.Div(id="kpi-user-tx-sum", className="user-kpi-box"),
                    html.Div(id="kpi-user-tx-avg", className="user-kpi-box"),
                    html.Div(id="kpi-user-card-count", className="user-kpi-box"),
                ],
                className="user-kpi-row"
            ),
            html.Div(  # Kreditlimit-Box EIGENE Zeile
                id="user-credit-limit-box",
                className="user-credit-limit-box"
            )
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
    return html.Div([
        html.I(className="bi bi-info-circle-fill ms-2", id="user-tab-info-icon"),
        dbc.Tooltip(
            "Enter a User ID or Card ID to update the information for the selected user or card.",
            target="user-tab-info-icon",
            placement="bottom",
            className="user-info-tooltip"
        )
    ])

def _create_top_kpis() -> html.Div:
    """
    Row with four KPI boxes (amount of transactions, total sum, avg, cards).
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
    Centered box for the credit limit (twice as wide as a KPI box).
    """
    return html.Div(
        id="user-credit-limit-box",
        children="Credit Limit",
        className="user-credit-limit-box"
    )
