from dash import html, dcc
from frontend.icon_manager import IconID, Icons

def create_user_content() -> html.Div:
    """
    Creates the content structure for the user tab.
    This includes search bars for name, user ID, card ID,
    the KPI boxes, and a placeholder for results.
    """
    return html.Div(
        children=[
            _create_search_bars(),
            _create_kpi_boxes_row(),
            _create_credit_limit_box(),
            html.Div(id='search-results', className="mt-4"),
        ],
        className="tab-content-inner"
    )

def _create_search_bars() -> html.Div:
    """
    Creates three search bars: by name, user ID, and card ID,
    each with a lens/search icon.
    """
    return html.Div(
        [
            _create_single_search_bar("user-id-search-input", "Search by User ID"),
            _create_single_search_bar("card-id-search-input", "Search by Card ID"),
        ],
        className="d-flex mb-4"
    )

def _create_single_search_bar(input_id: str, placeholder: str) -> html.Div:
    """
    Helper for a single search bar with icon.
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
        className="search-wrapper p-2 flex-grow-1 me-2" if "card-id" not in input_id else "search-wrapper p-2 flex-grow-1"
    )

def _create_kpi_boxes_row() -> html.Div:
    """
    Creates a row of four KPI boxes.
    """
    return html.Div(
        [
            html.Div(id="kpi-user-tx-count", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-sum", className="user-kpi-box"),
            html.Div(id="kpi-user-tx-avg", className="user-kpi-box"),
            html.Div(id="kpi-user-card-count", className="user-kpi-box"),
        ],
        className="d-flex justify-content-between mb-4"
    )

def _create_credit_limit_box() -> html.Div:
    """
    Creates a box for the user's credit limit.
    """
    return html.Div(
        id="user-credit-limit-box",
        children="Credit Limit",
        className="user-credit-limit-box my-2 mx-auto"
    )
