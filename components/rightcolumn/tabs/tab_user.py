from dash import html, dcc
from frontend.icon_manager import IconID, Icons
import dash_bootstrap_components as dbc

def create_user_content() -> html.Div:
    """
    Creates the content structure for the user tab.
    Heading: two search bars (User-ID, Card-ID) and an info icon/tooltip.
    Below: Platz für weitere Bereiche wie KPI-Boxen etc.
    """
    return html.Div(
        children=[
            _create_user_heading(),
            # Hier später weitere Bereiche (z.B. KPI-Boxen)
        ],
        className="tab-content-inner"
    )


def _create_user_heading() -> html.Div:
    """
    Heading mit zwei Suchleisten (User-ID, Card-ID) und Infobox.
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
    Eine Suchleiste mit Lupe.
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
    Info-Icon mit Tooltip (Infobox) – erklärt das Aktualisieren der Werte.
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

# --- Später fügst du unten weitere Bereiche wie KPI-Boxen ein ---
