import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, callback, callback_context

import components.constants as const
import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()

# Define the tab IDs and their corresponding content IDs
FRAUD_ANALYSIS_TABS = [
    (ID.FRAUD_ANALYSIS_TAB_OVERVIEW, ID.FRAUD_ANALYSIS_CONTENT_OVERVIEW),
    (ID.FRAUD_ANALYSIS_TAB_DEMOGRAPHICS, ID.FRAUD_ANALYSIS_CONTENT_DEMOGRAPHICS),
    (ID.FRAUD_ANALYSIS_TAB_PATTERNS, ID.FRAUD_ANALYSIS_CONTENT_PATTERNS),
    (ID.FRAUD_ANALYSIS_TAB_CARDS, ID.FRAUD_ANALYSIS_CONTENT_CARDS),
    (ID.FRAUD_ANALYSIS_TAB_MERCHANTS, ID.FRAUD_ANALYSIS_CONTENT_MERCHANTS),
]


# --- KPI: Total Fraud Cases ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_FRAUD_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_fraud_cases(_):
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    return f"{len(df_fraud):,}"


# --- KPI: Total Transactions ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_TRANSACTIONS_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_transactions(_):
    total_transactions = len(dm.df_transactions) if hasattr(dm, "df_transactions") else 0
    return f"{total_transactions:,}"


# --- KPI: Fraud Ratio (%) ---
@callback(
    Output(ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_ratio(_):
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    total_fraud = len(df_fraud)
    total_transactions = len(df)
    ratio = (total_fraud / total_transactions * 100) if total_transactions else 0
    return f"{ratio:.2f} %"


# --- Graph: Fraud Cases by US State (Bar & Line) ---
@callback(
    Output(ID.FRAUD_STATE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_state(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "merchant_state" not in df_fraud.columns or df_fraud.empty:
        return comp_factory.create_empty_figure()
    grouped = df_fraud.groupby("merchant_state").agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    )
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    grouped = grouped.sort_values(["costs"], ascending=False)
    fig = go.Figure()
    fig.add_bar(
        x=grouped.index, y=grouped["cases"],
        name="Fraud Cases",
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        yaxis="y1",
        hovertemplate="State: %{x}<br>Cases: %{y}<br>Total Cost: $%{customdata[0]:,.2f}<br>Avg Cost/Case: $%{customdata[1]:,.2f}",
        customdata=grouped[["costs", "avg_cost"]].values
    )
    fig.add_trace(go.Scatter(
        x=grouped.index, y=grouped["costs"],
        name="Total Fraud Amount",
        mode="lines+markers",
        marker_color="#EF553B",
        yaxis="y2"
    ))
    fig.update_layout(
        title="FRAUD BY STATE: NUMBER OF CASES & TOTAL AMOUNT",
        title_x=0.5,
        xaxis_title="STATE",
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            title="NUMBER OF FRAUD CASES",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            side="left"
        ),
        yaxis2=dict(
            title="TOTAL FRAUD AMOUNT ($)",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            overlaying="y",
            side="right"
        )
    )
    return fig


# --- Graph: Online vs. In-Store Fraud Cases (Pie Chart) ---
@callback(
    Output(ID.FRAUD_PIE_CHART, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_online_vs_inperson(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    # Setze is_online, falls nicht vorhanden
    if "is_online" not in df_fraud.columns and "merchant_city" in df_fraud.columns:
        df_fraud = df_fraud.copy()
        df_fraud.loc[:, "is_online"] = df_fraud["merchant_city"].isna() | (
                df_fraud["merchant_city"].str.lower() == "online")
    if not df_fraud.empty and "is_online" in df_fraud.columns:
        value_counts = df_fraud["is_online"].value_counts()
        labels = value_counts.index.map({True: "ONLINE", False: "IN-STORE"})
        fig = px.pie(
            names=labels,
            values=value_counts.values,
            color_discrete_sequence=[const.COLOR_ONLINE, const.COLOR_INSTORE]
        )
        fig.update_traces(
            textinfo='label+value+percent',
            textfont_size=16,
            textfont_color=text_color,
            textposition='inside'
        )
        fig.update_layout(
            title_x=0.5,
            paper_bgcolor=const.COLOR_TRANSPARENT,
            plot_bgcolor=const.COLOR_TRANSPARENT,
            font=dict(color=text_color),
            margin=dict(l=1, r=1, t=1, b=1),
            showlegend=False
        )
        return fig
    return comp_factory.create_empty_figure()


# --- Graph: Top 10 Online Merchants by Fraud Amount ---
@callback(
    Output(ID.FRAUD_TOP_MERCHANTS, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_top_merchants(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "is_online" not in df_fraud.columns and "merchant_city" in df_fraud.columns:
        df_fraud = df_fraud.copy()
        df_fraud.loc[:, "is_online"] = df_fraud["merchant_city"].isna() | (
                df_fraud["merchant_city"].str.lower() == "online")
    online_df = df_fraud[df_fraud["is_online"] == True]
    merchant_col = "merchant_name" if "merchant_name" in online_df.columns and online_df[
        "merchant_name"].notnull().any() else "merchant_id"
    if online_df.empty or merchant_col not in online_df.columns:
        return comp_factory.create_empty_figure()
    grouped = online_df.groupby(merchant_col).agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    ).sort_values("costs", ascending=False).head(10)
    bar_text = grouped["costs"].apply(lambda x: f"${x:,.0f}").values
    fig = px.bar(
        x=grouped.index.astype(str),
        y=grouped["cases"],
        labels={"x": "MERCHANT", "y": "NUMBER OF FRAUD CASES"},
        title="TOP 10 ONLINE MERCHANTS BY TOTAL FRAUD AMOUNT",
        text=bar_text
    )
    fig.update_traces(
        texttemplate='%{text}',
        textposition='inside',
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        textfont=dict(color=const.TEXT_COLOR_DARK)
    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title="MERCHANT",
        yaxis_title="NUMBER OF FRAUD CASES",
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        )
    )
    return fig


# --- Demographics: Fraud by Age Group (Bar & Line) ---
@callback(
    Output(ID.FRAUD_DEMO_AGE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_age(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    merged["age_group"] = pd.cut(
        merged["current_age"],
        bins=[0, 18, 25, 35, 45, 55, 65, 100],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']

    )
    grouped = merged.groupby("age_group", observed=False).agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    )
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    fig = go.Figure()
    fig.add_bar(
        x=grouped.index.astype(str), y=grouped["cases"],
        name="Fraud Cases",
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        yaxis="y1",
        hovertemplate="Age Group: %{x}<br>Cases: %{y}<br>Total Amount: $%{customdata[0]:,.2f}<br>Avg Amount/Case: $%{customdata[1]:,.2f}",
        customdata=grouped[["costs", "avg_cost"]].values
    )
    fig.add_trace(go.Scatter(
        x=grouped.index.astype(str), y=grouped["costs"],
        name="Total Fraud Amount",
        mode="lines+markers",
        marker_color="#EF553B",
        yaxis="y2"
    ))
    fig.update_layout(
        title="FRAUD BY AGE GROUP: NUMBER OF CASES & TOTAL AMOUNT",
        title_x=0.5,
        xaxis_title="AGE GROUP",
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            title="NUMBER OF FRAUD CASES",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            side="left"
        ),
        yaxis2=dict(
            title="TOTAL FRAUD AMOUNT ($)",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            overlaying="y",
            side="right"
        )
    )
    return fig


# --- Demographics: Fraud by Gender (Pie Chart & Summary) ---
@callback(
    Output(ID.FRAUD_DEMO_GENDER_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_gender(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    annotation_bg_color = "rgba(30,30,30,0.8)" if dark_mode else "white"
    annotation_border_color = "white" if dark_mode else "black"

    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    grouped = merged.groupby("gender", observed=False).agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    ).fillna(0)
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]

    fig = px.pie(
        names=grouped.index,
        values=grouped["cases"],
        title="FRAUD BY GENDER (NUMBER OF CASES)",
        color_discrete_sequence=[const.COLOR_FEMALE_PINK, const.COLOR_BLUE_MAIN]
    )
    fig.update_traces(
        textinfo='label+value',
        textfont_color=text_color
    )

    annotation_text = "<b>Totals:</b><br>"
    for gender, row in grouped.iterrows():
        annotation_text += (
            f"{gender}:<br>"
            f"&nbsp;&nbsp;Total Amount: ${row['costs']:,.2f}<br>"
            f"&nbsp;&nbsp;Avg Amount/Case: ${row['avg_cost']:,.2f}<br>"
        )
    fig.add_annotation(
        text=annotation_text,
        x=0, y=0.5, xref="paper", yref="paper",
        showarrow=False, align="left",
        bordercolor=annotation_border_color, borderwidth=1,
        bgcolor=annotation_bg_color,
        font=dict(size=13, color=text_color)
    )
    fig.update_layout(
        title_x=0.5,
        legend_title="GENDER",
        margin=dict(l=32, r=32, t=32, b=1),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color)
    )
    return fig


# --- Demographics: Fraud by Income (Violin Plot) ---
@callback(
    Output(ID.FRAUD_DEMO_INCOME_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_income(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")

    fig = px.violin(
        merged,
        y="yearly_income",
        box=True,
        points="all",
        color_discrete_sequence=[const.COLOR_BLUE_MAIN],
        title="FRAUD BY INCOME (DISTRIBUTION, OUTLIERS & MEDIAN)"
    )
    mean_income = merged["yearly_income"].mean()
    fig.add_hline(
        y=mean_income,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${mean_income:,.0f}",
        annotation_position="top right",
        annotation_font=dict(color=text_color)
    )
    median_income = merged["yearly_income"].median()
    fig.add_scatter(
        y=[median_income], x=[0],
        mode="markers",
        marker=dict(color="green", size=12, symbol="diamond"),
        name="Median"
    )
    fig.update_layout(
        title_x=0.5,
        yaxis_title="YEARLY INCOME ($)",
        showlegend=False,
        violingap=0.2,
        violingroupgap=0.3,
        violinmode='overlay',
        margin=dict(l=60, r=60, t=60, b=40),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        )
    )
    return fig


# --- Patterns: Fraud by Hour (Bar & Line) ---
@callback(
    Output(ID.FRAUD_PATTERN_HOUR_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_hour(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    df_fraud["hour"] = pd.to_datetime(df_fraud["date"]).dt.hour
    grouped = df_fraud.groupby("hour").agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    ).reindex(range(24), fill_value=0)
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    fig = go.Figure()
    fig.add_bar(
        x=grouped.index, y=grouped["cases"],
        name="Fraud Cases",
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        yaxis="y1",
        hovertemplate="Hour: %{x}<br>Cases: %{y}<br>Total Amount: $%{customdata[0]:,.2f}<br>Avg Amount/Case: $%{customdata[1]:,.2f}",
        customdata=grouped[["costs", "avg_cost"]].values
    )
    fig.add_trace(go.Scatter(
        x=grouped.index, y=grouped["costs"],
        name="Total Fraud Amount",
        mode="lines+markers",
        marker_color="#EF553B",
        yaxis="y2"
    ))
    fig.update_layout(
        title="FRAUD BY HOUR: NUMBER OF CASES & TOTAL AMOUNT",
        title_x=0.5,
        xaxis_title="HOUR OF DAY",
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            title="NUMBER OF FRAUD CASES",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            side="left"
        ),
        yaxis2=dict(
            title="TOTAL FRAUD AMOUNT ($)",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            overlaying="y",
            side="right"
        )
    )
    return fig


# --- Patterns: Fraud by Weekday (Bar & Line) ---
@callback(
    Output(ID.FRAUD_PATTERN_WEEKDAY_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_weekday(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    df_fraud["weekday"] = pd.to_datetime(df_fraud["date"]).dt.day_name()
    categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grouped = df_fraud.groupby("weekday").agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    ).reindex(categories, fill_value=0)
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    fig = go.Figure()
    fig.add_bar(
        x=grouped.index, y=grouped["cases"],
        name="Fraud Cases",
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        yaxis="y1",
        hovertemplate="Day: %{x}<br>Cases: %{y}<br>Total Amount: $%{customdata[0]:,.2f}<br>Avg Amount/Case: $%{customdata[1]:,.2f}",
        customdata=grouped[["costs", "avg_cost"]].values
    )
    fig.add_trace(go.Scatter(
        x=grouped.index, y=grouped["costs"],
        name="Total Fraud Amount",
        mode="lines+markers",
        marker_color="#EF553B",
        yaxis="y2"
    ))
    fig.update_layout(
        title="FRAUD BY WEEKDAY: NUMBER OF CASES (BAR) & TOTAL AMOUNT",
        title_x=0.5,
        xaxis_title="WEEKDAY",
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            title="NUMBER OF FRAUD CASES",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            side="left"
        ),
        yaxis2=dict(
            title="TOTAL FRAUD AMOUNT ($)",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            overlaying="y",
            side="right"
        )
    )
    return fig


# --- Patterns: Fraud Transaction Amounts (Box Plot) ---
@callback(
    Output(ID.FRAUD_PATTERN_AMOUNT_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_amount(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    fig = px.box(df_fraud, y="amount", points="all", title="FRAUD TRANSACTION AMOUNTS", color_discrete_sequence=[const.COLOR_BLUE_MAIN])
    fig.update_layout(
        title_x=0.5,
        yaxis_title="FRAUD TRANSACTION AMOUNT ($)",
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        )
    )
    return fig


# --- Cards & Merchants: Fraud by Card Type (Bar) ---
@callback(
    Output(ID.FRAUD_CARD_TYPE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_type(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    cards = dm.df_cards
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(cards, left_on="card_id", right_on="id", how="left")
    card_counts = merged["card_type"].value_counts()
    total_amount = merged["amount"].sum()
    amount_per_type = merged.groupby("card_type")["amount"].sum().reindex(card_counts.index).fillna(0)
    bar_text = [f"{count:,} Cases<br>${amt:,.2f}" for count, amt in zip(card_counts.values, amount_per_type.values)]
    fig = px.bar(
        x=card_counts.index, y=card_counts.values,
        labels={"x": "CARD TYPE", "y": "NUMBER OF FRAUD CASES"},
        title=f"FRAUD BY CARD TYPE<br><sup>TOTAL FRAUD AMOUNT: ${total_amount:,.2f}</sup>",
        text=bar_text
    )
    fig.update_traces(
        textposition='inside',
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95,
        textfont=dict(color=const.TEXT_COLOR_DARK)
    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title="CARD TYPE",
        yaxis_title="NUMBER OF FRAUD CASES",
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        barcornerradius="16%",
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        )
    )
    return fig


# --- Cards & Merchants: Fraud by Card Brand (Pie Chart) ---
@callback(
    Output(ID.FRAUD_CARD_BRAND_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_brand(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT

    df = dm.df_transactions
    cards = dm.df_cards
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(cards, left_on="card_id", right_on="id", how="left")
    brand_counts = merged["card_brand"].value_counts()
    fig = px.pie(
        names=brand_counts.index,
        values=brand_counts.values,
        title="FRAUD BY CARD BRAND"
    )
    fig.update_traces(
        textinfo='label+value',
        textfont_color=text_color,
        textposition='inside'
    )
    fig.update_layout(
        title_x=0.5,
        legend_title="CARD BRAND",
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=1)
    )
    return fig


# --- Cards & Merchants: Top 10 Merchant Categories by Fraud Amount (Bar & Line) ---
# TODO: Automatically, not hardcoded
mcc_map = {
    "4829": "Wire Transfer Money Orders",
    "5912": "Pharmacies",
    "5411": "Supermarkets",
    "5300": "Wholesale Clubs",
    "5311": "Department Stores",
    "5541": "Service Stations",
    "4900": "Utilities",
    "4814": "Telecommunication Services",
    "7538": "Automotive Service Shops",
    "5499": "Miscellaneous Food Stores"
}


def get_mcc_name(mcc_code, mcc_map):
    code_str = str(mcc_code)
    return mcc_map.get(code_str, f"Unknown ({code_str})")


@callback(
    Output(ID.FRAUD_MCC_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_mcc(app_state):
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "mcc" not in df_fraud.columns or df_fraud.empty:
        return comp_factory.create_empty_figure()
    grouped = df_fraud.groupby("mcc").agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    )
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    grouped = grouped.sort_values("costs", ascending=False).head(10)
    grouped.index = grouped.index.map(lambda x: get_mcc_name(x, mcc_map))
    fig = px.line(
        grouped,
        x=grouped.index,
        y="costs",
        markers=True,
        title="TOP 10 MERCHANT CATEGORIES BY TOTAL FRAUD AMOUNT",
        labels={"x": "MERCHANT CATEGORY", "costs": "TOTAL FRAUD AMOUNT ($)"}
    )
    fig.update_traces(mode="lines+markers", marker_color="#EF553B")
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        plot_bgcolor=const.COLOR_TRANSPARENT,
        font=dict(color=text_color),
        margin=dict(l=32, r=32, t=32, b=32),
        xaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color)
        )
    )
    return fig


@callback(
    [Output(tab_id, "className") for tab_id, _ in FRAUD_ANALYSIS_TABS],
    [Output(content_id, "className") for _, content_id in FRAUD_ANALYSIS_TABS],
    [Input(tab_id, "n_clicks") for tab_id, _ in FRAUD_ANALYSIS_TABS]
)
def update_fraud_analysis_tabs(*n_clicks_list):
    ctx = callback_context

    if not ctx.triggered:
        # Default to the first tab (Overview) if no button has been clicked
        active_tab_id = ID.FRAUD_ANALYSIS_TAB_OVERVIEW
    else:
        # Get the ID of the button that was clicked
        active_tab_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Button classes
    btn_classes = [
        "custom-tab-button active" if tab_id == active_tab_id else "custom-tab-button"
        for tab_id, _ in FRAUD_ANALYSIS_TABS
    ]

    # Content classes
    content_classes = [
        "tab-item active" if tab_id == active_tab_id else "tab-item hidden"
        for tab_id, content_id in FRAUD_ANALYSIS_TABS
    ]

    return btn_classes + content_classes
