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
    Input(ID.SETTING_MAP_TEXT_COLOR, "value"),
    Input(ID.SETTING_MAP_SHOW_COLOR_SCALE, "value"),
    Input(ID.SETTING_GENERAL_SHOW_TOOLTIPS, "value"),
    Input(ID.SETTING_GENERAL_CANVAS_PLACEMENT, "value"),
    State(ID.APP_STATE_STORE, "data"),
)
def update_app_state(_, n_clicks_dark, map_color_scale, map_text_color, map_show_color_scale, show_tooltips,
                     canvas_placement, current_state):
    """
    Updates and synchronizes the application state based on user interactions or
    initial load. This function reacts to various input triggers to modify the app
    state, including dark mode toggling, map settings adjustments, tooltip
    visibility, and canvas placement. It ensures that visual elements are
    dynamically updated to reflect the current state while maintaining the
    integrity of the state store.

    Args:
        _: Placeholder for the "children" property of the app-init trigger. Not used.
        n_clicks_dark: Number of clicks on the dark mode toggle button. Used to toggle dark mode.
        map_color_scale: Selected color scale for the map.
        map_text_color: Selected text color for the map.
        map_show_color_scale: Boolean indicating whether to show the map's color scale.
        show_tooltips: Boolean indicating whether tooltips should be shown.
        canvas_placement: Placement option for the settings canvas.
        current_state: The current state of the application, stored in a JSON object.

    Returns:
        A tuple containing:
        - The className for the settings canvas, dynamically updated based on the dark mode state.
        - The className for the dashboard container, dynamically updated based on the dark mode state.
        - The children property of the dark mode toggle button, updated with the appropriate icon.
        - The updated application state as a JSON object.
    """
    # Context determination
    triggered_id = ctx.triggered_id if ctx.triggered_id else "app-init-trigger"

    # Initialize state if necessary
    if current_state is None:
        current_state = const.APP_STATE_STORE_DEFAULT

    # Update state based on trigger
    if triggered_id == ID.BUTTON_DARK_MODE_TOGGLE.value and n_clicks_dark:
        current_state["dark_mode"] = not current_state.get("dark_mode", const.DEFAULT_DARK_MODE)
        current_state["settings_changed"] = True
        current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_MAP_COLOR_SCALE.value:
        if current_state.get("map_setting_color_scale") != map_color_scale:
            current_state["map_setting_color_scale"] = map_color_scale
            current_state["settings_changed"] = True
            current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_MAP_TEXT_COLOR.value:
        if current_state.get("map_setting_text_color") != map_text_color:
            current_state["map_setting_text_color"] = map_text_color
            current_state["settings_changed"] = True
            current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_MAP_SHOW_COLOR_SCALE.value:
        if current_state.get("map_setting_show_color_scale") != map_show_color_scale:
            current_state["map_setting_show_color_scale"] = map_show_color_scale
            current_state["settings_changed"] = True
            current_state["update_id"] += 1

    elif triggered_id == ID.SETTING_GENERAL_SHOW_TOOLTIPS.value:
        if current_state.get("general_setting_show_tooltips") != show_tooltips:
            current_state["general_setting_show_tooltips"] = show_tooltips
            current_state["settings_changed"] = False

    elif triggered_id == ID.SETTING_GENERAL_CANVAS_PLACEMENT.value:
        if current_state.get("general_setting_canvas_placement") != canvas_placement:
            current_state["general_setting_canvas_placement"] = canvas_placement
            current_state["settings_changed"] = False

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
    Renders the map based on the application's animation state and current settings.
    Triggered only during the specific phase of animation ("fading_out"). Ensures
    the map updates accordingly with the settings stored in the app state, including
    dark mode, color scale, and text color preferences. Updates the app state once
    the map is rendered.

    Args:
        animation_state: A dictionary containing the state of the animation, necessary
            to determine if the map rendering should proceed.
        app_state: A dictionary storing the application's state, including various
            configuration settings for the map, such as dark mode and color scale.

    Returns:
        A tuple containing the following:
            - The rendered map component.
            - The updated class name for the map container, which includes the fade-in
              effect when the map is rendered.
            - The updated application state, ensuring the state reflects any modifications
              (such as resetting the settings_changed flag).

    Raises:
        PreventUpdate: If animation_state or app_state is invalid, or if the animation phase
            is not "fading_out", the rendering process is aborted and updates are prevented.
    """
    if not animation_state or not app_state:
        raise PreventUpdate

    # Only render when we are in the correct phase
    if animation_state.get("phase") != "fading_out":
        raise PreventUpdate

    # Render map with current settings
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE)
    color_scale = app_state.get("map_setting_color_scale", const.MAP_DEFAULT_COLOR_SCALE)
    text_color = app_state.get("map_setting_text_color", const.TEXT_COLOR_LIGHT if dark_mode else const.TEXT_COLOR_DARK)
    show_color_scale = app_state.get("map_setting_show_color_scale", const.MAP_DEFAULT_SHOW_COLOR_SCALE)

    map_style = "carto-darkmatter-nolabels" if dark_mode else "carto-positron-nolabels"
    map_component = create_usa_map(color_scale=color_scale, text_color=text_color, map_style=map_style,
                                   dark_mode=dark_mode, show_color_scale=show_color_scale)

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


# === INITIALIZE SETTINGS COMPONENTS ===
@callback(
    Output(ID.SETTING_MAP_COLOR_SCALE, "value"),
    Output(ID.SETTING_MAP_TEXT_COLOR, "value"),
    Output(ID.SETTING_MAP_SHOW_COLOR_SCALE, "value"),
    Output(ID.SETTING_GENERAL_SHOW_TOOLTIPS, "value"),
    Output(ID.SETTING_GENERAL_CANVAS_PLACEMENT, "value"),
    Input("layout-ready-signal", "children"),
    State(ID.APP_STATE_STORE, "data"),
    prevent_initial_call=True,
)
def initialize_settings_components(ready_signal, app_state):
    """
    Initializes the settings components with values from the application state.

    This callback is triggered when the layout is ready and ensures that all settings
    components display the correct values from the application state, rather than
    their default values.

    Args:
        ready_signal: Signal to indicate readiness for initialization. Expected value
            is "ready".
        app_state: The current state of the application containing settings values.

    Returns:
        tuple: A tuple containing the values for each settings component, retrieved
        from the application state.

    Raises:
        PreventUpdate: If the ready signal is not "ready" or the app state is None.
    """
    if ready_signal != "ready" or app_state is None:
        raise PreventUpdate

    # Get values from app state with defaults as fallback
    color_scale = app_state.get("map_setting_color_scale", const.MAP_DEFAULT_COLOR_SCALE)
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE)
    text_color = app_state.get("map_setting_text_color", "black" if dark_mode else "white")
    show_color_scale = app_state.get("map_setting_show_color_scale", const.MAP_DEFAULT_SHOW_COLOR_SCALE)
    show_tooltips = app_state.get("general_setting_show_tooltips", True)
    canvas_placement = app_state.get("general_setting_canvas_placement", "start")

    return color_scale, text_color, show_color_scale, show_tooltips, canvas_placement
