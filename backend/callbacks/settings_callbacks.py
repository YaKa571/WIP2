import time

from dash import callback, Output, Input, State, MATCH, ctx, html
from dash.exceptions import PreventUpdate

from backend.data_manager import DataManager
from components.factories.component_factory import create_usa_map
from frontend.component_ids import ID

dm = DataManager.get_instance()


# === SETTINGS CANVAS TOGGLE ===
@callback(
    Output(ID.SETTINGS_CANVAS.value, "is_open"),
    Input(ID.BUTTON_SETTINGS_MENU.value, "n_clicks"),
    State(ID.SETTINGS_CANVAS.value, "is_open")
)
def toggle_settings_canvas(n_clicks, is_open):
    return not is_open if n_clicks else is_open


# === CENTRAL APP STATE MANAGER ===
@callback(
    Output(ID.SETTINGS_CANVAS.value, "className"),
    Output(ID.DASHBOARD_CONTAINER.value, "className"),
    Output(ID.BUTTON_DARK_MODE_TOGGLE.value, "children"),
    Output(ID.APP_STATE_STORE.value, "data"),
    Input("app-init-trigger", "children"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE.value, "n_clicks"),
    Input(ID.SETTING_MAP_COLOR_SCALE.value, "value"),
    State(ID.APP_STATE_STORE.value, "data"),
)
def update_app_state(_, n_clicks, color_scale, current_state):
    # Context determination
    triggered_id = ctx.triggered_id if ctx.triggered_id else "app-init-trigger"

    # Initialize state if necessary
    if current_state is None:
        current_state = {
            "dark_mode": False,
            "color_scale": color_scale if color_scale else "Viridis",  # Default value
            "phase": "initial",
            "update_id": 0,
            "settings_changed": True
        }

    # Update state based on trigger
    if triggered_id == ID.BUTTON_DARK_MODE_TOGGLE.value and n_clicks:
        current_state["dark_mode"] = not current_state.get("dark_mode", False)
        current_state["settings_changed"] = True
        current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_MAP_COLOR_SCALE.value:
        if current_state.get("color_scale") != color_scale:
            current_state["color_scale"] = color_scale
            current_state["settings_changed"] = True
            current_state["update_id"] += 1

    # Read dark mode status
    dark = current_state.get("dark_mode", False)

    # Update UI classes and icon
    canvas_cls = "settings-canvas dark-mode" if dark else "settings-canvas"
    dash_cls = "dashboard dark-mode" if dark else "dashboard"
    icon = html.I(className=f"bi bi-{'moon-fill' if dark else 'sun-fill'}")

    return canvas_cls, dash_cls, icon, current_state


# === FIRST STEP: START LOADING ANIMATION ===
@callback(
    Output(ID.MAP_CONTAINER.value, "className"),
    Output(ID.ANIMATION_STATE_STORE.value, "data"),
    Input(ID.APP_STATE_STORE.value, "data"),
    State(ID.ANIMATION_STATE_STORE.value, "data"),
)
def prepare_map_update(app_state, animation_state):
    if not app_state:
        raise PreventUpdate

    # Initialize if necessary
    if animation_state is None:
        animation_state = {
            "last_update_id": -1,
            "phase": "not_started"
        }

    # If no settings changes exist, do nothing
    if not app_state.get("settings_changed", False) and app_state.get("update_id", 0) == animation_state.get(
            "last_update_id", -1):
        raise PreventUpdate

    # Remember update ID
    animation_state["last_update_id"] = app_state.get("update_id", 0)
    animation_state["phase"] = "fading_out"

    # Start fade-out (shows loading circle)
    return "map-container fade-out", animation_state


# === SECOND STEP: RENDER MAP ===
@callback(
    Output(ID.MAP_CONTAINER.value, "children"),
    Output(ID.MAP_CONTAINER.value, "className", allow_duplicate=True),
    Output(ID.APP_STATE_STORE.value, "data", allow_duplicate=True),
    Input(ID.ANIMATION_STATE_STORE.value, "data"),
    State(ID.APP_STATE_STORE.value, "data"),
    prevent_initial_call=True
)
def render_map(animation_state, app_state):
    if not animation_state or not app_state:
        raise PreventUpdate

    # Only render when we are in the correct phase
    if animation_state.get("phase") != "fading_out":
        raise PreventUpdate

    # Render map with current settings
    dark = app_state.get("dark_mode", False)
    color_scale = app_state.get("color_scale", "blues")

    mapbox_style = "carto-darkmatter" if dark else "carto-positron"
    map_component = create_usa_map(color_scale=color_scale, mapbox_style=mapbox_style)

    # Reset settings changed flag
    app_state["settings_changed"] = False

    # Map-Component, Fade-In Class, updated App-State
    return map_component, "map-container fade-in", app_state


# === FIRST RENDER (AT START) ===
@callback(
    Output("layout-ready-signal", "children"),
    Input("app-init-trigger", "children"),
)
def initialize_layout(_):
    # A short delay to ensure the layout is fully loaded
    time.sleep(0.1)
    return "ready"


# === START RENDERING THE MAP ===
@callback(
    Output(ID.APP_STATE_STORE.value, "data", allow_duplicate=True),
    Input("layout-ready-signal", "children"),
    State(ID.APP_STATE_STORE.value, "data"),
    prevent_initial_call=True,
)
def trigger_initial_render(ready_signal, app_state):
    if ready_signal != "ready" or app_state is None:
        raise PreventUpdate

    # Ensure rendering also happens on the first load
    app_state["settings_changed"] = True
    app_state["phase"] = "ready_to_render"

    return app_state


# === TOOLTIP TOGGLE ===
@callback(
    Output({"type": "tooltip", "id": MATCH}, "style"),
    Input(ID.SETTING_GENERAL_SHOW_TOOLTIPS.value, "value")
)
def toggle_tooltips(show):
    return {} if show else {"display": "none"}


@callback(Output(ID.SETTINGS_CANVAS.value, "placement"),
          Input(ID.SETTING_GENERAL_CANVAS_PLACEMENT.value, "value")
          )
def change_settings_position(placement):
    return placement
