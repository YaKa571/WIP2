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
AGE_GROUP_COLORS = [
    "#00b894",
    "#00cec9",
    "#0984e3",
    "#6c5ce7",
    "#fdcb6e",
    "#e17055",
    "#d35400",
    "#636e72",
    "#b2bec3",
]
GRAPH_GRID_COLOR_DARK = "rgba(230,230,230,0.11)"
GRAPH_GRID_COLOR_LIGHT = "rgba(25,25,25,0.11)"
COLOR_TRANSPARENT = "rgba(0,0,0,0)"

# Bools
DEFAULT_DARK_MODE: bool = True

# Stores
APP_STATE_STORE_DEFAULT = {
            "dark_mode": DEFAULT_DARK_MODE,
            "color_scale": "blues",
            "phase": "initial",
            "update_id": 0,
            "settings_changed": False
        }


# Paths
DATA_DIRECTORY = Path("assets/data/")
