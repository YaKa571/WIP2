from dash import callback, Output, Input, State, html

from frontend.component_ids import IDs


@callback(
    Output(IDs.DASHBOARD_CONTAINER.value, "className"),
    Output(IDs.DARK_MODE_TOGGLE.value, "children"),
    Output(IDs.MAP.value, "figure"),
    Input(IDs.DARK_MODE_TOGGLE.value, "n_clicks"),
    State(IDs.DASHBOARD_CONTAINER.value, "className"),
    State(IDs.MAP.value, "figure"),
)
def toggle_dark_mode(n_clicks, current_class, current_fig):
    if not n_clicks:
        return current_class or "dashboard", html.I(className="bi bi-sun-fill"), current_fig

    is_dark = "dark-mode" in current_class

    if is_dark:
        # Switch to light
        new_class = "dashboard"
        new_icon = html.I(className="bi bi-sun-fill")
        new_style = "carto-positron"
    else:
        # Switch to dark
        new_class = "dashboard dark-mode"
        new_icon = html.I(className="bi bi-moon-fill")
        new_style = "carto-darkmatter"

    # Update only the mapbox.style in the existing figure
    current_fig["layout"]["mapbox"]["style"] = new_style

    return new_class, new_icon, current_fig
