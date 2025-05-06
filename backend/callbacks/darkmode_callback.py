from dash import callback, Output, Input, State, html

from frontend.component_ids import IDs


@callback(
    Output(IDs.DARK_MODE_STORE.value, "data"),
    Output(IDs.DASHBOARD_CONTAINER.value, "className"),
    Output(IDs.DARK_MODE_TOGGLE.value, "children"),
    Output(IDs.MAP.value, "figure"),
    Input(IDs.DARK_MODE_TOGGLE.value, "n_clicks"),
    State(IDs.DARK_MODE_STORE.value, "data"),
    State(IDs.MAP.value, "figure")
)
def toggle_dark_mode(n_clicks, is_dark, current_fig):
    """
    Toggles the dark mode for the dashboard application.

    This callback function manages the dark mode state, UI components' className, the icon
    for the dark mode toggle, and the map styling within the application. It switches between
    dark and light modes based on user interaction and updates corresponding elements
    accordingly.

    Parameters
    ----------
    n_clicks: int
        The number of times the dark mode toggle button has been clicked.
    is_dark: bool
        The current state of the dark mode (True for dark mode, False for light mode).
    current_fig: dict
        The current figure (map) data used in the application.

    Returns
    -------
    tuple[bool, str, dash_html_components.I, dict]
        A tuple containing the updated dark mode state as a boolean, the updated className
        as a string for the dashboard container, an html.I element representing the icon,
        and the updated map figure as a dictionary.
    """
    # On first load keep stored value, else flip it
    new_dark = is_dark if not n_clicks else not is_dark

    # Map className, icon class and map style from new_dark
    cls = "dashboard dark-mode" if new_dark else "dashboard"
    icon_name = "moon-fill" if new_dark else "sun-fill"
    map_style = "carto-darkmatter" if new_dark else "carto-positron"

    # Update mapbox style
    current_fig["layout"]["mapbox"]["style"] = map_style

    # Return new store value, className, icon and updated figure
    return (
        new_dark,
        cls,
        html.I(className=f"bi bi-{icon_name}"),
        current_fig
    )
