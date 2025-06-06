# Add constants here...
from pathlib import Path

# Colors
COLOR_BLUE_MAIN = "#2563eb"
COLOR_FEMALE_PINK = "#c65ed4"
TEXT_COLOR_LIGHT = "#222c3a"
TEXT_COLOR_DARK = "#e0e6ed"
GREEN_LIGHT = "#259d60"
GREEN_DARK = "#81C784"
COLOR_ONLINE = "#00bcd4"
COLOR_INSTORE = "#fb8c00"
COLOR_ORANGE = "#ff9800"
AGE_GROUP_COLORS = {
    "10-20": "#16a085",  # dark green/teal
    "20-30": "#2980b9",  # strong blue
    "30-40": "#34495e",  # dark gray-blue
    "40-50": "#8e44ad",  # strong violet
    "50-60": "#e67e22",  # orange, not too bright
    "60-70": "#c0392b",  # reddish brown
    "70-80": "#7f8c8d",  # dark gray
    "80-90": "#d35400",  # rust orange
    "90-100": "#2d3436",  # very dark gray
    "100-110": "#6c5ce7",  # violet
}
GRAPH_GRID_COLOR_DARK = "rgba(230,230,230,0.11)"
GRAPH_GRID_COLOR_LIGHT = "rgba(25,25,25,0.11)"
COLOR_TRANSPARENT = "rgba(0,0,0,0)"
CLUSTER_COLORS = {
    "0": "#56B4E9",  # light blue
    "1": "#D55E00",  # reddish brown
    "2": "#009E73",  # teal green
    "3": "#E69F00",  # orange
    "4": "#0072B2",  # dark blue
    "5": "#F0E442",  # yellow
    "6": "#CC79A7",  # pink/magenta
    "7": "#999999",  # grey
    "8": "#ADFF2F",  # light green
    "9": "#87CEEB"  # sky blue
}

# Bools
DEFAULT_DARK_MODE: bool = True

# Map
MAP_DEFAULT_COLOR_SCALE = "burg"
MAP_DEFAULT_SHOW_COLOR_SCALE = True

# Stores
APP_STATE_STORE_DEFAULT = {
    "dark_mode": DEFAULT_DARK_MODE,
    "map_setting_color_scale": MAP_DEFAULT_COLOR_SCALE,
    "map_setting_text_color": "black" if DEFAULT_DARK_MODE else "white",
    "map_setting_show_color_scale": MAP_DEFAULT_SHOW_COLOR_SCALE,
    "general_setting_show_tooltips": True,
    "general_setting_canvas_placement": "start",
    "phase": "initial",
    "update_id": 0,
    "settings_changed": False
}

# Paths
DATA_DIRECTORY = Path("assets/data/")
CACHE_DIRECTORY = Path("assets/data/cache/")
