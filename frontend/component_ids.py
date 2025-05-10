from enum import Enum

class IDs(str, Enum):

    APP_STATE_STORE = "app-state-store"
    ANIMATION_STATE_STORE = "animation-state-store"

    KPI_CARD_AMT_TRANSACTIONS = "kpi-card-amt-transactions"
    KPI_CARD_SUM_OF_TRANSACTIONS = "kpi-card-sum-of-transactions"
    KPI_CARD_AVG_TRANSACTION_AMOUNT = "kpi-card-avg-transaction-amount"

    TABS_BAR = "tabs-bar"
    TAB_HOME = "tab-home"
    TAB_FRAUD = "tab-fraud"
    TAB_CLUSTER = "tab-cluster"
    TAB_USER = "tab-user"
    TAB_MERCHANT = "tab-merchant"
    TAB_TEST = "tab-test"

    TABLE_CARDS = "table-cards"
    TABLE_TRANSACTIONS = "table-transactions"
    TABLE_USERS = "table-users"
    TABLE_MCC = "table-mcc"

    MAP = "map"
    MAP_CONTAINER = "map-container"  # Used for callback
    MAP_SPINNER = "map-spinner"

    BUTTON_DARK_MODE_TOGGLE = "button-dark-mode-toggle"
    DASHBOARD_CONTAINER = "dashboard-container"

    # Settings
    SETTINGS_CANVAS = "settings-canvas"
    BUTTON_SETTINGS_MENU = "button-settings-menu"
    SETTINGS_CARD_GENERAL = "settings-card-general"
    SETTINGS_CARD_MAP = "settings-card-map"
    SETTING_MAP_COLOR_SCALE = "setting-map-color-scale"
    SETTING_GENERAL_SHOW_TOOLTIPS = "setting-general-show-tooltips"
    SETTING_GENERAL_CANVAS_PLACEMENT = "setting-general-canvas-placement"

    # Cluster
    CLUSTER_DROPDOWN = "cluster-dropdown"
    CLUSTER_DROPDOWN_OUTPUT = "cluster-dropdown-output"