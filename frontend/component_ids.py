from enum import Enum

class ID(str, Enum):

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

    # Home Tab
    HOME_KPI_MOST_VALUABLE_MERCHANT = "home-kpi-most-valuable-merchant"
    HOME_KPI_TOP_SPENDING_USER = "home-kpi-top-spending-user"
    HOME_KPI_MOST_VISITED_MERCHANT = "home-kpi-most-visited-merchant"
    HOME_KPI_PEAK_HOUR = "home-kpi-peak-hour"
    HOME_GRAPH_EXPENDITURES_BY_GENDER = "home-graph-expenditures-by-gender"
    HOME_GRAPH_EXPENDITURES_BY_CHANNEL = "home-graph-expenditures-by-channel"
    HOME_GRAPH_EXPENDITURES_BY_AGE = "home-graph-expenditures-by-age"
    HOME_TAB_SELECTED_STATE_STORE = "home-tab-selected-state-store"
    HOME_TAB_STATE_HEADING = "home-tab-state-heading"
    HOME_TAB_BUTTON_TOGGLE_ALL_STATES = "home-tab-button-toggle-all-states"
    HOME_TAB_INFO_ICON = "home-tab-info-icon"
    HOME_TAB_BAR_CHART_DROPDOWN = "home-tab-bar-chart-dropdown"
    HOME_GRAPH_BAR_CHART = "home-graph-bar-chart"

    # Fraud Tab

    # Cluster Tab
    CLUSTER_DROPDOWN = "cluster-dropdown"
    CLUSTER_LEGEND = "cluster-legend"
    CLUSTER_GRAPH = "cluster-graph"
    CLUSTER_HEADING = "cluster-heading"
    CLUSTER_INFO_ICON = "cluster-info-icon"
    CLUSTER_DEFAULT_SWITCH = "cluster-default-switch"
    CLUSTER_DEFAULT_SWITCH_CONTAINER = "cluster-default-switch-container" #needed for invisibility

    # User Tab
    # TODO @Son: Add IDs here
    USER_TAB_INFO_ICON = "user-tab-info-icon"

    # Merchant Tab
    MERCHANT_ID_SEARCH = "merchant-id-search"
    MERCHANT_HEADING = "merchant-heading"
    MERCHANT_INFO_ICON = "merchant-info-icon"
    MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP = "merchant-kpi-most-frequently-merchant"
    MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP = "merchant-kpi-high-value-merchant"