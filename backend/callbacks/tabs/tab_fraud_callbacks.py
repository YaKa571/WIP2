import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from dash import Input, Output, callback
from frontend.component_ids import ID
from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_fraud_data_setup import (
    fraud_by_state_bar,
    online_transaction_share_pie,
    top_online_merchants
)

# --- KPI: Total Fraud Cases ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_FRAUD_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_fraud_cases(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    return f"{len(df_fraud):,}"

# --- KPI: Total Transactions ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_TRANSACTIONS_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_transactions(_):
    dm = DataManager.get_instance()
    total_transactions = len(dm.df_transactions) if hasattr(dm, "df_transactions") else 0
    return f"{total_transactions:,}"

# --- KPI: Fraud Ratio (%) ---
@callback(
    Output(ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_ratio(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    total_fraud = len(df_fraud)
    total_transactions = len(df)
    ratio = (total_fraud / total_transactions * 100) if total_transactions else 0
    return f"{ratio:.2f} %"

# --- Graph: Fraud Transactions by State ---
@callback(
    Output(ID.FRAUD_STATE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_state(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    state_counts = df_fraud['merchant_state'].value_counts().reset_index()
    state_counts.columns = ['merchant_state', 'transaction_count']
    fig = px.bar(
        state_counts,
        x='merchant_state',
        y='transaction_count',
        title='Fraud Transactions per US State',
        labels={'merchant_state': 'State', 'transaction_count': 'Transaction Count'}
    )
    return fig

# --- Graph: Online vs. In-Person Fraud (Pie Chart) ---
@callback(
    Output(ID.FRAUD_PIE_CHART, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_online_vs_inperson(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if not df_fraud.empty:
        return online_transaction_share_pie(df_fraud)
    return go.Figure()

# --- Graph: Top Online Merchants by Fraud Count ---
@callback(
    Output(ID.FRAUD_TOP_MERCHANTS, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_top_merchants(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if not df_fraud.empty:
        try:
            return top_online_merchants(df_fraud)
        except Exception as e:
            print("Fehler in top_online_merchants:", e)
            return go.Figure()
    return go.Figure()

# --- Demographics ---
@callback(
    Output(ID.FRAUD_DEMO_AGE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_age(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    merged["age_group"] = pd.cut(
        merged["current_age"],
        bins=[0, 18, 30, 45, 60, 100],
        labels=["<18", "18-30", "31-45", "46-60", "60+"]
    )
    age_counts = merged["age_group"].value_counts().sort_index()
    fig = px.bar(
        x=age_counts.index, y=age_counts.values,
        labels={"x": "Age Group", "y": "Number of Fraud Transactions"},
        title="Fraud by Age Group"
    )
    fig.update_layout(xaxis_title="Age Group", yaxis_title="Number of Fraud Transactions")
    return fig

@callback(
    Output(ID.FRAUD_DEMO_GENDER_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_gender(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    fig = px.pie(
        merged, names="gender", title="Fraud by Gender"
    )
    fig.update_layout(legend_title="Gender")
    return fig

@callback(
    Output(ID.FRAUD_DEMO_INCOME_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_income(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    fig = px.box(
        merged, y="yearly_income", points="all", title="Fraud by Income"
    )
    fig.update_layout(yaxis_title="Yearly Income")
    return fig

# --- Patterns ---
@callback(
    Output(ID.FRAUD_PATTERN_HOUR_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_hour(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    df_fraud["hour"] = pd.to_datetime(df_fraud["date"]).dt.hour
    hour_counts = df_fraud["hour"].value_counts().sort_index()
    fig = px.bar(
        x=hour_counts.index, y=hour_counts.values,
        labels={"x": "Hour of Day", "y": "Number of Fraud Transactions"},
        title="Fraud by Hour of Day"
    )
    fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Number of Fraud Transactions")
    return fig

@callback(
    Output(ID.FRAUD_PATTERN_WEEKDAY_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_weekday(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    df_fraud["weekday"] = pd.to_datetime(df_fraud["date"]).dt.day_name()
    categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = df_fraud["weekday"].value_counts().reindex(categories, fill_value=0)
    fig = px.bar(
        x=weekday_counts.index, y=weekday_counts.values, title="Fraud by Weekday"
    )
    fig.update_layout(xaxis_title="Weekday", yaxis_title="Number of Fraud Transactions")
    return fig

@callback(
    Output(ID.FRAUD_PATTERN_AMOUNT_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_amount(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    fig = px.box(df_fraud, y="amount", points="all", title="Fraud Transaction Amounts")
    fig.update_layout(yaxis_title="Fraud Transaction Amount")
    return fig

# --- Cards & Merchants ---
@callback(
    Output(ID.FRAUD_CARD_TYPE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_type(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    cards = dm.df_cards
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(cards, left_on="card_id", right_on="id", how="left")
    card_counts = merged["card_type"].value_counts()
    fig = px.bar(
        x=card_counts.index, y=card_counts.values,
        labels={"x": "Card Type", "y": "Number of Fraud Transactions"},
        title="Fraud by Card Type"
    )
    fig.update_layout(xaxis_title="Card Type", yaxis_title="Number of Fraud Transactions")
    return fig

@callback(
    Output(ID.FRAUD_CARD_BRAND_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_brand(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    cards = dm.df_cards
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(cards, left_on="card_id", right_on="id", how="left")
    fig = px.pie(
        merged, names="card_brand", title="Fraud by Card Brand"
    )
    fig.update_layout(legend_title="Card Brand")
    return fig

@callback(
    Output(ID.FRAUD_MCC_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_mcc(_):
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    top_mcc = df_fraud["mcc"].value_counts().nlargest(10).index
    filtered = df_fraud[df_fraud["mcc"].isin(top_mcc)]
    mcc_counts = filtered["mcc"].value_counts()
    fig = px.bar(
        x=mcc_counts.index, y=mcc_counts.values,
        labels={"x": "Merchant Category Code (MCC)", "y": "Number of Fraud Transactions"},
        title="Top Merchant Categories (MCC) by Fraud Count"
    )
    fig.update_layout(xaxis_title="Merchant Category Code (MCC)", yaxis_title="Number of Fraud Transactions")
    return fig