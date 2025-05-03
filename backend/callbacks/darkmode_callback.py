from dash import callback, Output, Input, State, html

from frontend.component_ids import IDs


@callback(
    Output(IDs.DASHBOARD_CONTAINER.value, "className"),
    Output(IDs.DARK_MODE_TOGGLE.value, "children"),
    Input(IDs.DARK_MODE_TOGGLE.value, "n_clicks"),
    State(IDs.DASHBOARD_CONTAINER.value, "className")
)
def toggle_dark_mode(n_clicks, current_class):
    if not n_clicks:
        return current_class or "dashboard", html.I(className="bi bi-sun-fill")

    is_dark = "dark-mode" in current_class
    if is_dark:
        # Switch to light-mode
        return "dashboard", html.I(className="bi bi-sun-fill")
    else:
        # Switch to dark-mode
        return "dashboard dark-mode", html.I(className="bi bi-moon-fill")
