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
    """
    Callback function to update the total fraud cases displayed in the Fraud KPI section.

    This function listens to changes in the application state and calculates the
    number of fraudulent transactions based on the presence of non-null and
    non-empty error fields in the transaction data. The result is returned as a
    formatted string with commas as thousand separators.

    Args:
        _: Dummy argument to satisfy the callback input signature. The value is
           provided automatically by Dash's callback mechanism and represents the
           application state data.

    Returns:
        str: A formatted string representing the total number of fraud cases with
        commas as thousand separators.
    """
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    return f"{len(df_fraud):,}"


# --- KPI: Total Transactions ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_TRANSACTIONS_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_transactions(_):
    """
    Updates the display for the total number of transactions.

    This callback function listens for changes in the application state store
    and updates the total transactions count displayed on the corresponding UI
    element. It calculates the count based on the presence and length of the
    `df_transactions` attribute in the `dm` object.

    Args:
        _: Data from the application state that triggers this callback.

    Returns:
        str: Formatted string representing the total transactions count.
    """
    total_transactions = len(dm.df_transactions) if hasattr(dm, "df_transactions") else 0
    return f"{total_transactions:,}"


# --- KPI: Fraud Ratio (%) ---
@callback(
    Output(ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_ratio(_):
    """
    Updates and returns the fraud ratio percentage based on the number of fraudulent
    transactions and total transactions in the data.

    The fraud ratio is calculated as the percentage of fraudulent transactions over
    the total transactions. If there are no transactions, the ratio is set to 0.

    Args:
        _: Dict[str, Any]
            The application state data, passed automatically by the callback
            mechanism, but not specifically utilized in the function.

    Returns:
        str:
            The fraud ratio as a formatted string with two decimal places followed
            by a percentage sign, such as "12.34 %".
    """
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
    """
    Updates and returns a Plotly figure displaying fraud data by state. The figure includes
    a bar chart of the number of fraud cases per state and a line chart showing the total
    fraud amount. It adapts the colors and styles based on the application's dark mode setting.

    Args:
        app_state (dict): Dictionary containing application state data. It must include
            a "dark_mode" key if dark mode settings are to be considered. If not provided,
            default settings are used.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object combining a bar chart and line
        chart with styling and hover capabilities. If no data is available, an empty figure
        is returned.
    """
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
    """
    Updates the pie chart visualization displaying the distribution of fraud occurrences
    between online and in-person transactions based on the provided application state.
    The function dynamically adjusts the chart's appearance based on the app's dark mode
    setting and creates a pie chart using transaction data, categorized as online or
    in-store.

    Args:
        app_state (dict or None): The current application state containing
            configurations such as dark mode. If `app_state` is None, default
            values for configurations will be used.

    Returns:
        Plotly.graph_objs._figure.Figure: A plotly Figure object representing the
            pie chart. If no relevant fraud data is found, an empty figure is returned.
    """
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
    """
    Updates and returns a bar chart figure displaying the top 10 online merchants based on
    the total fraud amount. The figure is styled according to the application's dark mode
    setting and displays the number of fraud cases per merchant.

    Args:
        app_state: dict. The application state, containing information such as whether dark
            mode is enabled. If not provided, default values are used.

    Returns:
        plotly.graph_objects.Figure: A bar chart figure showing the top 10 online merchants
        by total fraud amount, with corresponding fraud case counts.
    """
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
        text=bar_text,
        template="plotly_dark" if dark_mode else "plotly_white"  # <- NEU
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
    """
    Updates a graph displaying fraud cases and total fraud amount by age group.

    This callback function is responsible for generating a plotly figure that shows
    the number of fraudulent transactions and total fraudulent amounts segmented
    by age groups. It uses the application's state to configure visual preferences
    such as dark mode and retrieves data from predefined data sources for analysis.
    The generated plot contains a bar graph for the number of fraud cases and a line
    graph for the total fraud amount overlaid within the same figure.

    Args:
        app_state: A dictionary containing the current state of the application.
            Includes configurations such as dark mode.

    Returns:
        plotly.graph_objects.Figure: A figure that visualizes the number of fraud cases
        and total fraud amount by age group.
    """
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    df = dm.df_transactions
    users = dm.df_users

    merged_all = df.merge(users, left_on="client_id", right_on="id", how="left")
    merged_all["age_group"] = pd.cut(
        merged_all["current_age"],
        bins=[0, 18, 25, 35, 45, 55, 65, 100],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    )
    trans_count = merged_all.groupby("age_group", observed=False).size().rename("transaction_count")

    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")].copy()
    merged_fraud = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")
    merged_fraud["age_group"] = pd.cut(
        merged_fraud["current_age"],
        bins=[0, 18, 25, 35, 45, 55, 65, 100],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    )
    grouped_fraud = merged_fraud.groupby("age_group", observed=False).agg(
        fraud_cases=("amount", "count")
    )

    combined = pd.concat([trans_count, grouped_fraud], axis=1).fillna(0)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=combined.index.astype(str),
        y=combined["transaction_count"],
        name="Total Transactions",
        mode="lines+markers",
        marker=dict(color="grey"),
        yaxis="y1",
        hovertemplate="Age Group: %{x}<br>Total Transactions: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=combined.index.astype(str),
        y=combined["fraud_cases"],
        name="Fraud Cases",
        mode="lines+markers",
        marker=dict(color=const.COLOR_BLUE_MAIN),
        yaxis="y1",
        hovertemplate="Age Group: %{x}<br>Fraud Cases: %{y}<extra></extra>",
    ))

    fig.update_layout(
        title="FRAUD BY AGE GROUP: NUMBER OF CASES & TOTAL TRANSACTIONS",
        title_x=0.5,
        xaxis_title="AGE GROUP",
        legend=dict(x=0.01, y=0.99),
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
            title="NUMBER OF FRAUD CASES & TRANSACTIONS",
            gridcolor=grid_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            side="left"
        )
    )

    return fig




# --- Demographics: Fraud by Gender (Pie Chart & Summary) ---
@callback(
    Output(ID.FRAUD_DEMO_GENDER_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_gender(app_state):
    """
    Updates the fraud by gender pie chart figure based on the application state.

    The function calculates the number of fraud cases, total fraud costs, and average
    fraud cost per case for each gender. It generates a pie chart visualizing the number
    of fraud cases by gender and includes additional data annotations displaying aggregate
    statistics for each gender. The appearance of the chart adapts to the application's
    dark mode settings.

    Args:
        app_state (dict or None): The current state of the application. It provides
            configuration parameters such as whether dark mode is enabled. If None,
            default values are used for configuration.

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure object representing a pie chart
        of fraud cases by gender, along with annotations detailing fraud statistics.
    """
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
    """
    Updates the fraud-by-income graph by creating a violin plot that visualizes the
    distribution, outliers, and median of yearly incomes of users associated with fraudulent
    transactions. The visualization updates based on the application's dark mode settings.

    Args:
        app_state (dict): The current state of the application, which includes settings
            such as dark mode.

    Returns:
        plotly.graph_objects.Figure: A violin plot figure showing the income distribution
            among users with fraudulent transactions. Includes indicators for the mean and
            median yearly incomes.
    """
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
    fig.add_trace(
    go.Scatter(
        y=[median_income],
        x=[0],  
        mode="markers",
        marker=dict(color="green", size=12, symbol="diamond"),
        name="Median"
    )
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
    """
    Updates the fraud by hour graph figure based on the application state. The graph visualizes the number of fraud cases
    and the total fraud amounts by each hour of the day, using bar and line chart representations respectively. The figure
    adjusts its appearance dynamically based on the dark mode setting provided in the application state.

    Args:
        app_state (dict): A dictionary representing the current application state, containing various configuration
            options. It includes the key `dark_mode` (a boolean indicating whether dark mode is enabled), with a default
            fallback value if not provided.

    Returns:
        plotly.graph_objs.Figure: A Plotly figure object displaying the fraud by hour graph with configured layout,
        colors, and data visualization elements.
    """
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
    fig.add_trace(go.Bar(
    x=grouped.index,
    y=grouped["cases"],
    name="Fraud Cases",
    marker_color=const.COLOR_BLUE_MAIN,
    marker_line_width=0,
    opacity=0.95,
    yaxis="y1",
    hovertemplate="Hour: %{x}<br>Cases: %{y}<br>Total Amount: $%{customdata[0]:,.2f}<br>Avg Amount/Case: $%{customdata[1]:,.2f}",
    customdata=grouped[["costs", "avg_cost"]].values
    ))
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
    """
    Generates a Plotly figure illustrating the number of fraudulent cases and
    the total fraud amount across weekdays, based on transaction data.

    This function processes data from the application state to determine
    whether dark mode is enabled. Based on dark mode or light mode, it selects
    appropriate color schemes for gridlines, text, and other graphical
    elements. It filters and groups transaction data to calculate weekday-based
    statistics such as fraud cases, total fraud costs, and the average fraud cost
    per case. The resulting figure contains a bar graph of fraud cases alongside
    a line plot of total fraud amounts.

    Args:
        app_state (dict): The current application state data, which contains a
            "dark_mode" key indicating whether dark mode is active. If `app_state`
            is `None`, default values are used.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object visualizing fraud cases
        and total fraud costs by weekday.
    """
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
    fig.add_trace(go.Bar(
    x=grouped.index,
    y=grouped["cases"],
    name="Fraud Cases",
    marker_color=const.COLOR_BLUE_MAIN,
    marker_line_width=0,
    opacity=0.95,
    yaxis="y1",
    hovertemplate="Day: %{x}<br>Cases: %{y}<br>Total Amount: $%{customdata[0]:,.2f}<br>Avg Amount/Case: $%{customdata[1]:,.2f}",
    customdata=grouped[["costs", "avg_cost"]].values
    ))
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
    """
    Updates the figure of the fraud transaction amount box plot based on the application
    state. It filters the fraudulent transactions from the dataset and creates a box
    plot with appropriate formatting and coloring based on the application's dark mode
    setting.

    Args:
        app_state (dict): The application state data from a dashboard store. It should
            include the "dark_mode" key to determine UI color mode preferences. If
            unavailable, a default value is used.

    Returns:
        plotly.graph_objects.Figure: The updated box plot figure visualizing fraudulent
            transaction amounts with configurations suitable for the current UI mode.
    """
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
    """
    Updates and returns a Plotly bar chart visualization of the fraud distribution by card type.

    This function processes the transactional data and card metadata to generate a bar chart
    representing the number of fraud cases by card type, along with the aggregated fraud amount.
    It dynamically adjusts the chart appearance based on the dark mode setting stored in the app state.

    Args:
        app_state (Optional[dict]): A dictionary containing the application state data. It is used to
            determine the dark mode state to adjust the chart's visual properties, such as text color and grid color.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object representing the bar chart of fraud cases by card type.
    """
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
    """
    Updates the fraud by card brand pie chart figure based on the provided application
    state by analyzing transaction and card data. The function prepares a pie chart
    displaying the count of fraudulent transactions categorized by card brand. The
    appearance of the chart (e.g., text color) adapts based on the application's dark
    mode setting.

    Args:
        app_state: The current application state, provided as a dictionary. It contains
            information such as the dark mode setting. If None, default settings are used.

    Returns:
        plotly.graph_objects.Figure: A pie chart figure that visualizes fraudulent
            transaction counts by card brand, styled dynamically based on application state.
    """
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

def get_mcc_name(mcc_code, mcc_map):
    """
    Fetches the MCC (Merchant Category Code) name from the provided MCC map.

    This function takes an MCC code and a mapping of MCC codes to their names.
    It returns the corresponding name if the MCC code is found in the map. If the
    MCC code is not found, it returns a default string indicating the code is unknown.

    Args:
        mcc_code (int or str): The MCC (Merchant Category Code) to look up.
            It can be provided as either an integer or a string.
        mcc_map (dict): A dictionary mapping MCC codes (as strings) to their
            respective names.

    Returns:
        str: The name corresponding to the given MCC code if found in the map.F
            If the MCC code is not present in the map, a string indicating
            "Unknown" along with the MCC code is returned.
    """
    code_str = str(mcc_code)
    return mcc_map.get(code_str, f"Unknown ({code_str})")



@callback(
    Output(ID.FRAUD_MCC_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_mcc(app_state):
    """
    Generates a line chart visualization displaying the top 10 merchant categories
    with the highest total fraud amount based on transaction data. The data includes
    cases of errors or fraudulent activity, grouped by merchant category code (MCC).
    The chart dynamically adapts visual styling according to the selected dark mode
    preference.

    Args:
        app_state (dict): Application state data containing user preferences, including
            dark mode settings.

    Returns:
        plotly.graph_objects.Figure: A Plotly line chart figure depicting the top
        merchant categories ranked by total fraud amount, with styling adapted to
        the dark mode preference. If no fraud data is available, an empty figure
        is returned.
    """
    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]

    if "mcc" not in df_fraud.columns or df_fraud.empty:
        return go.Figure()

    mcc_map = dict(zip(dm.df_mcc["mcc"].astype(str), dm.df_mcc["merchant_group"]))

    grouped = df_fraud.groupby("mcc").agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    )
    grouped["avg_cost"] = grouped["costs"] / grouped["cases"]
    grouped = grouped.sort_values("costs", ascending=False).head(10)
    grouped.index = grouped.index.map(lambda x: get_mcc_name(x, mcc_map))

    fig = px.bar(
        grouped,
        x=grouped.index,
        y="costs",
        title="Top 10 Merchant Categories by Total Fraud Amount (Bar Chart)",
        labels={"x": "Merchant Category", "costs": "Total Fraud Amount ($)"}
    )
    fig.update_traces(
        marker_color=const.COLOR_BLUE_MAIN,
        marker_line_width=0,
        opacity=0.95
    )
    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly",
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




@callback(
    [Output(tab_id, "className") for tab_id, _ in FRAUD_ANALYSIS_TABS],
    [Output(content_id, "className") for _, content_id in FRAUD_ANALYSIS_TABS],
    [Input(tab_id, "n_clicks") for tab_id, _ in FRAUD_ANALYSIS_TABS]
)
def update_fraud_analysis_tabs(*n_clicks_list):
    """
    Updates the class names for fraud analysis tabs and their associated content based on the
    button click. It dynamically determines which tab and content should be displayed as active
    while marking others as inactive or hidden.

    This function ensures that the active state is visually highlighted for the currently
    selected tab while hiding the content for non-active tabs.

    Args:
        *n_clicks_list: A variable-length argument that represents the number of clicks for
            each tab button. This input determines the active tab based on the triggered
            button's click.

    Returns:
        list[str]: A list of class names for both tabs and tab content, determining their
            visibility and active state. The returned list combines button class names
            indicating their active/inactive state and content class names indicating
            visibility or hidden state.
    """
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