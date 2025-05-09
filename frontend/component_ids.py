from enum import Enum

class IDs(str, Enum):
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

    DARK_MODE_TOGGLE = "dark-mode-toggle"
    DARK_MODE_STORE = "dark-mode-store"
    DASHBOARD_CONTAINER = "dashboard-container"