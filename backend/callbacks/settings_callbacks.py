import time

from dash import callback, Output, Input, State, MATCH, ctx, html
from dash.exceptions import PreventUpdate

import components.constants as const
from backend.data_manager import DataManager
from components.factories.component_factory import create_usa_map
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()


# === SETTINGS CANVAS TOGGLE ===
@callback(
    Output(ID.SETTINGS_CANVAS.value, "is_open"),
    Input(ID.BUTTON_SETTINGS_MENU.value, "n_clicks"),
    State(ID.SETTINGS_CANVAS.value, "is_open")
)
def toggle_settings_canvas(n_clicks, is_open):
    """
    Toggles the visibility of the settings canvas in response to user interaction with
    the settings menu button.

    Args:
        n_clicks (int): The number of times the settings menu button has been clicked.
        is_open (bool): A boolean indicating the current open state of the settings canvas.

    Returns:
        bool: The updated open state of the settings canvas.
    """
    return not is_open if n_clicks else is_open


# === CENTRAL APP STATE MANAGER ===
@callback(
    Output(ID.SETTINGS_CANVAS, "className"),
    Output(ID.DASHBOARD_CONTAINER, "className"),
    Output(ID.BUTTON_DARK_MODE_TOGGLE, "children"),
    Output(ID.APP_STATE_STORE, "data"),
    Input("app-init-trigger", "children"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
    Input(ID.SETTING_MAP_COLOR_SCALE, "value"),
    State(ID.APP_STATE_STORE, "data"),
)
def update_app_state(_, n_clicks, color_scale, current_state):
    """
    Handles the state updates and UI toggling based on user interaction with the application.
    The function processes different types of inputs to determine the current state and modifies
    the return values for output components accordingly.

    Args:
        _: Ignored value, represents the content of the 'app-init-trigger'. Typically, not used.
        n_clicks: Number of clicks on the dark mode toggle button. Used to determine if the mode
            should be switched between dark and light.
        color_scale: Selected color scale for the map visualization. Changes trigger updates in
            the application’s state to align with the new color scale.
        current_state: Persisted state data of the application. Includes various state elements
            such as dark mode status, color scale, update count, and settings modification flag.

    Returns:
        tuple: A tuple containing:
            - canvas_cls (str): CSS class name for the settings canvas, updated based on the
              current dark mode status.
            - dash_cls (str): CSS class name for the dashboard container, updated based on the
              current dark mode status.
            - icon (html.I): An HTML icon element representing the current state of the dark mode
              toggle button (moon for dark mode, sun for light mode).
            - updated_state (dict): Updated dictionary containing the new state of the application.
    """
    # Context determination
    triggered_id = ctx.triggered_id if ctx.triggered_id else "app-init-trigger"

    # Initialize state if necessary
    if current_state is None:
        current_state = {
            "dark_mode": const.DEFAULT_DARK_MODE,
            "color_scale": color_scale if color_scale else "Viridis",  # Default value
            "phase": "initial",
            "update_id": 0,
            "settings_changed": True
        }

    # Update state based on trigger
    if triggered_id == ID.BUTTON_DARK_MODE_TOGGLE.value and n_clicks:
        current_state["dark_mode"] = not current_state.get("dark_mode", const.DEFAULT_DARK_MODE)
        current_state["settings_changed"] = True
        current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_MAP_COLOR_SCALE.value:
        if current_state.get("color_scale") != color_scale:
            current_state["color_scale"] = color_scale
            current_state["settings_changed"] = True
            current_state["update_id"] += 1

    # Read dark mode status
    dark = current_state.get("dark_mode", const.DEFAULT_DARK_MODE)

    # Update UI classes and icon
    canvas_cls = "settings-canvas dark-mode" if dark else "settings-canvas"
    dash_cls = "dashboard dark-mode" if dark else "dashboard"
    icon = html.I(className=f"bi bi-{'moon-fill' if dark else 'sun-fill'}")

    return canvas_cls, dash_cls, icon, current_state


# === FIRST STEP: START LOADING ANIMATION ===
@callback(
    Output(ID.MAP_CONTAINER, "className"),
    Output(ID.ANIMATION_STATE_STORE, "data"),
    Input(ID.APP_STATE_STORE, "data"),
    State(ID.ANIMATION_STATE_STORE, "data"),
)
def prepare_map_update(app_state, animation_state):
    """
    Handles updates to the map based on the application and animation states. This function is triggered by a callback
    when the application state or animation state changes. If settings have changed or a new update is required,
    the map will begin a fade-out phase and the animation state is updated accordingly.

    Args:
        app_state: The current state of the application, provided by a storage component. Expected to be a dictionary with
            possible keys like 'settings_changed' (bool) and 'update_id' (int).
        animation_state: The current state of animations, provided by a storage component. Expected to be a dictionary with
            keys like 'last_update_id' (int) and 'phase' (str). Can be None during the initial execution.

    Returns:
        Tuple:
            The first element is a string representing the CSS class name for the map container, typically
            indicating the fade-out transition. The second element is an updated version of the animation state
            dictionary.

    Raises:
        PreventUpdate: Raised when there is no need to update, either because the application state is missing, settings
            haven't changed, or no new update is required.
    """
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
    Output(ID.MAP_CONTAINER, "children"),
    Output(ID.MAP_CONTAINER, "className", allow_duplicate=True),
    Output(ID.APP_STATE_STORE, "data", allow_duplicate=True),
    Input(ID.ANIMATION_STATE_STORE, "data"),
    State(ID.APP_STATE_STORE, "data"),
    prevent_initial_call=True
)
def render_map(animation_state, app_state):
    """
    Handles the rendering of the map component with specified settings and updates the application
    state accordingly. This function listens to changes in the animation state and application state,
    and only updates the map when the application is in the correct phase.

    Args:
        animation_state (dict): The current state of the animation, including the phase of the
            animation process.
        app_state (dict): The current application state, which includes settings such as dark mode,
            color scale, and flags for setting changes.

    Returns:
        tuple: A tuple containing the following elements:
            - The map component to render.
            - The class names to be applied to the map container, enabling specific CSS animations
              or styles.
            - The updated application state.

    Raises:
        PreventUpdate: If the animation state or application state is invalid or if the phase of
        the animation is not "fading_out", no update will be triggered.
    """
    if not animation_state or not app_state:
        raise PreventUpdate

    # Only render when we are in the correct phase
    if animation_state.get("phase") != "fading_out":
        raise PreventUpdate

    # Render map with current settings
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE)
    color_scale = app_state.get("color_scale", "blues")

    map_style = "carto-darkmatter-nolabels" if dark_mode else "carto-positron-nolabels"
    map_component = create_usa_map(color_scale=color_scale, map_style=map_style, dark_mode=dark_mode)

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
    """
    Initializes the application layout and signifies its readiness.

    This function ensures that the layout setup is complete by introducing a
    short delay before returning a readiness signal. The delay accounts for
    any asynchronous loading or rendering that might be occurring internally.

    Args:
        _: Placeholder input used to trigger the initialization process.
           This value is not used within the function.

    Returns:
        str: A string signal ("ready") indicating that the layout is fully
             initialized and ready for use.
    """
    time.sleep(0.1)
    return "ready"


# === START RENDERING THE MAP ===
@callback(
    Output(ID.APP_STATE_STORE, "data", allow_duplicate=True),
    Input("layout-ready-signal", "children"),
    State(ID.APP_STATE_STORE, "data"),
    prevent_initial_call=True,
)
def trigger_initial_render(ready_signal, app_state):
    """
    Triggers the initial rendering of the application layout once the application state
    is ready. It listens for a signal indicating that the application is ready to proceed
    and modifies the app state accordingly to ensure rendering happens.

    Args:
        ready_signal: Signal to indicate readiness for initial rendering. Expected value
            is "ready".
        app_state: The current state of the application containing settings and phase
            data.

    Returns:
        dict: The updated application state with changes to facilitate initial rendering.
    """
    if ready_signal != "ready" or app_state is None:
        raise PreventUpdate

    # Ensure rendering also happens on the first load
    app_state["settings_changed"] = True
    app_state["phase"] = "ready_to_render"

    return app_state


# === TOOLTIP TOGGLE ===
@callback(
    Output({"type": "tooltip", "id": MATCH}, "style"),
    Input(ID.SETTING_GENERAL_SHOW_TOOLTIPS, "value")
)
def toggle_tooltips(show):
    """
    Toggles the display of tooltips based on input value.

    This function is used as a callback in a Dash application to manage
    the visibility of tooltips. If the input value indicates that tooltips
    should be shown, it returns an empty dictionary to make the tooltip
    visible. Otherwise, it returns a dictionary setting the tooltip's
    "display" style to "none," effectively hiding it.

    Args:
        show (bool): A boolean value indicating whether tooltips should
            be shown (True) or hidden (False).

    Returns:
        dict: A dictionary containing the CSS style to apply to the
            tooltips. If showing tooltips, returns an empty dictionary.
            If hiding tooltips, returns {"display": "none"}.
    """
    return {} if show else {"display": "none"}


@callback(Output(ID.SETTINGS_CANVAS, "placement"),
          Input(ID.SETTING_GENERAL_CANVAS_PLACEMENT, "value")
          )
def change_settings_position(placement):
    """
    Updates the canvas placement based on the provided input.

    This callback function updates the 'placement' attribute of the settings canvas
    based on the current value provided through the input component. The returned
    value will directly modify the configuration of the settings canvas to reflect
    the user's desired placement.

    Args:
        placement: The new placement value for the settings canvas as provided by
            the input.

    Returns:
        The updated placement value for the settings canvas.
    """
    return placement
