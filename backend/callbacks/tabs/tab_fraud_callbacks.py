import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from dash import Input, Output, callback
from frontend.component_ids import ID
from backend.data_manager import DataManager

# --- KPI: Total Fraud Cases ---
@callback(
    Output(ID.FRAUD_KPI_TOTAL_FRAUD_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_total_fraud_cases(_):
    """
    Updates the total number of fraud cases displayed on the application.

    This callback function calculates the total number of fraud cases in the
    current dataset and updates the specified UI component with the calculated
    value. Fraud cases are determined based on the presence of non-empty "errors"
    in the dataset.

    Args:
        _: Ignored parameter used to trigger the callback when the application
           state is updated.

    Returns:
        str: A formatted string representing the total number of fraud cases,
        with commas as thousand separators.
    """
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
    """
    Updates and returns the total number of transactions to be displayed in the fraud KPI
    dashboard. This function extracts the transaction data from the global application state via
    a data manager instance, calculates the total number of transactions, and formats it as a
    human-readable string with commas as thousand separators.

    Args:
        _: Placeholder input parameter to correspond with Dash callback dependencies, not used
            in the computation.

    Returns:
        str: The total number of transactions formatted as a string with commas separating
            thousands.
    """
    dm = DataManager.get_instance()
    total_transactions = len(dm.df_transactions) if hasattr(dm, "df_transactions") else 0
    return f"{total_transactions:,}"

# --- KPI: Fraud Ratio (%) ---
@callback(
    Output(ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID, "children"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_ratio(_):
    """
    Updates the fraud ratio KPI display. This callback function calculates the percentage
    of fraudulent transactions from the total transactions and returns the calculated
    value as a formatted string.

    Args:
        _: Unused parameter included to match the callback's input signature. It takes
            the value of 'data' from the APP_STATE_STORE input.

    Returns:
        str: The fraud ratio as a formatted string with two decimal places followed by
            a percent symbol (e.g., '12.34 %').
    """
    dm = DataManager.get_instance()
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
def update_fraud_by_state(_):
    """
    Updates the fraud statistics by state visualization in the form of a bar and
    line chart. The bar chart represents the number of fraud cases by state, while
    the line chart displays the total fraud amount. The chart includes hover
    information detailing the total cost and average cost per fraud case for each
    state.

    Args:
        _: Any input data, typically unused but required for the callback mechanism.

    Returns:
        A Plotly Figure object containing the fraud statistics visualization by
        state. If no fraud cases are found in the data, returns an empty figure.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "merchant_state" not in df_fraud.columns or df_fraud.empty:
        return go.Figure()
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
        marker_color="#636EFA",
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
        title="Fraud by State: Number of Cases (Bar) & Total Amount (Line)",
        xaxis_title="State",
        yaxis=dict(title="Number of Fraud Cases", side="left"),
        yaxis2=dict(title="Total Fraud Amount ($)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99)
    )
    return fig

# --- Graph: Online vs. In-Store Fraud Cases (Pie Chart) ---
@callback(
    Output(ID.FRAUD_PIE_CHART, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_online_vs_inperson(_):
    """
    Updates the pie chart visualization displaying the distribution of fraud cases
    as either online or in-person based on the data stored in the application state.

    Args:
        _: Any input placeholder value. This input value is not used directly
           by the function but is required for callback structure in the framework.

    Returns:
        plotly.graph_objects.Figure: A pie chart visualization providing a
        breakdown of fraud case occurrences categorized as either online or
        in-store. If no valid data is available, returns an empty figure.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    # Setze is_online, falls nicht vorhanden
    if "is_online" not in df_fraud.columns and "merchant_city" in df_fraud.columns:
        df_fraud = df_fraud.copy()  
        df_fraud.loc[:, "is_online"] = df_fraud["merchant_city"].isna() | (df_fraud["merchant_city"].str.lower() == "online")
    if not df_fraud.empty and "is_online" in df_fraud.columns:
        value_counts = df_fraud["is_online"].value_counts()
        labels = value_counts.index.map({True: "Online", False: "In-Store"})
        fig = px.pie(
            names=labels,
            values=value_counts.values,
            title="Fraud Cases: Online vs. In-Store"
        )
        fig.update_traces(
            textinfo='label+value+percent',
            textfont_size=16
        )
        return fig
    return go.Figure()

# --- Graph: Top 10 Online Merchants by Fraud Amount ---
@callback(
    Output(ID.FRAUD_TOP_MERCHANTS, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_top_merchants(_):
    """
    Updates the top merchants chart data based on the application's state. This
    function processes the transaction data to identify fraudulent online
    transactions, aggregates the data by merchant, and generates a bar chart of
    the top 10 online merchants with the highest total fraud amounts.

    Args:
        _: Unused placeholder for the input data, typically representing the
            application's state store information.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure representing a bar chart of
        the top 10 online merchants by total fraud amount, including textual data
        for the fraud amount displayed on each bar. Returns an empty figure if
        there is no adequate data available to process.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "is_online" not in df_fraud.columns and "merchant_city" in df_fraud.columns:
        df_fraud = df_fraud.copy()
        df_fraud.loc[:, "is_online"] = df_fraud["merchant_city"].isna() | (df_fraud["merchant_city"].str.lower() == "online")
    online_df = df_fraud[df_fraud["is_online"] == True]
    merchant_col = "merchant_name" if "merchant_name" in online_df.columns and online_df["merchant_name"].notnull().any() else "merchant_id"
    if online_df.empty or merchant_col not in online_df.columns:
        return go.Figure()
    grouped = online_df.groupby(merchant_col).agg(
        cases=("amount", "count"),
        costs=("amount", "sum")
    ).sort_values("costs", ascending=False).head(10)
    bar_text = grouped["costs"].apply(lambda x: f"${x:,.0f}").values
    fig = px.bar(
        x=grouped.index.astype(str),
        y=grouped["cases"],
        labels={"x": "Merchant", "y": "Number of Fraud Cases"},
        title="Top 10 Online Merchants by Total Fraud Amount",
        text=bar_text
    )
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        marker_color="#636EFA"
    )
    fig.update_layout(
        xaxis_title="Merchant",
        yaxis_title="Number of Fraud Cases"
    )
    return fig

# --- Demographics: Fraud by Age Group (Bar & Line) ---
@callback(
    Output(ID.FRAUD_DEMO_AGE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_age(_):
    """
    Updates the figure displaying fraud statistics segmented by age group. It computes
    various metrics, including the count of fraud cases, total fraud amount, and average
    cost per fraud case for each age group, and generates a Plotly figure combining bar
    and line plots for visualization.

    Args:
        _: Unused parameter that receives data from the application state store.

    Returns:
        plotly.graph_objects.Figure: A bar and line plot representing fraud statistics
        by age group. The bar chart shows the number of fraud cases, and the line chart
        shows the total fraud amount. Secondary information, like average fraud cost per
        case, is included in the hover tooltips.
    """
    dm = DataManager.get_instance()
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
        marker_color="#636EFA",
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
        title="Fraud by Age Group: Number of Cases (Bar) & Total Amount (Line)",
        xaxis_title="Age Group",
        yaxis=dict(title="Number of Fraud Cases", side="left"),
        yaxis2=dict(title="Total Fraud Amount ($)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99)
    )
    return fig

# --- Demographics: Fraud by Gender (Pie Chart & Summary) ---
@callback(
    Output(ID.FRAUD_DEMO_GENDER_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_gender(_):
    """
    Generates and updates a pie chart figure representing cases and associated
    costs of fraud categorized by gender. The function retrieves transaction
    and user data, processes them to compute the necessary metrics, and builds
    a visual representation of fraud distribution.

    Args:
        _: dict
            Placeholder for Input `ID.APP_STATE_STORE, "data"`. This input is not
            utilized in the function directly but required for callback compatibility.

    Returns:
        plotly.graph_objects.Figure
            A pie chart showing fraud cases by gender with annotations that include
            total and average costs per gender.
    """
    dm = DataManager.get_instance()
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
        title="Fraud by Gender (Number of Cases)"
    )
    fig.update_traces(textinfo='label+value')

    annotation_text = "<b>Totals:</b><br>"
    for gender, row in grouped.iterrows():
        annotation_text += (
            f"{gender}:<br>"
            f"&nbsp;&nbsp;Total Amount: ${row['costs']:,.2f}<br>"
            f"&nbsp;&nbsp;Avg Amount/Case: ${row['avg_cost']:,.2f}<br>"
        )
    fig.add_annotation(
        text=annotation_text,
        x=1.15, y=0.5, xref="paper", yref="paper",
        showarrow=False, align="left",
        bordercolor="black", borderwidth=1, bgcolor="white", font=dict(size=13)
    )
    fig.update_layout(
        legend_title="Gender",
        margin=dict(r=120)
    )
    return fig

# --- Demographics: Fraud by Income (Violin Plot) ---
@callback(
    Output(ID.FRAUD_DEMO_INCOME_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_income(_):
    """
    Updates the fraud distribution graph by income.

    This callback function generates a violin plot visualization of income
    distribution among fraud cases using transaction and user data from the
    DataManager singleton instance. It computes and highlights the statistical
    mean and median of yearly income for fraud cases. The plot provides insights
    into the distribution, outliers, and key statistics of fraud by income.

    Args:
        _: Placeholder for callback input data, typically provided by the state
            store defined in the Input decorator.

    Returns:
        plotly.graph_objects.Figure: A configured violin plot figure object
        visualizing fraud by income distribution, including mean and median
        annotations.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    users = dm.df_users
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(users, left_on="client_id", right_on="id", how="left")

    fig = px.violin(
        merged,
        y="yearly_income",
        box=True,
        points="all",
        color_discrete_sequence=["#636EFA"],
        title="Fraud by Income (Distribution, Outliers & Median)"
    )
    mean_income = merged["yearly_income"].mean()
    fig.add_hline(
        y=mean_income,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${mean_income:,.0f}",
        annotation_position="top right"
    )
    median_income = merged["yearly_income"].median()
    fig.add_scatter(
        y=[median_income], x=[0],
        mode="markers",
        marker=dict(color="green", size=12, symbol="diamond"),
        name="Median"
    )
    fig.update_layout(
        yaxis_title="Yearly Income ($)",
        showlegend=False,
        violingap=0.2,
        violingroupgap=0.3,
        violinmode='overlay',
        margin=dict(l=60, r=60, t=60, b=40)
    )
    return fig

# --- Patterns: Fraud by Hour (Bar & Line) ---
@callback(
    Output(ID.FRAUD_PATTERN_HOUR_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_hour(_):
    """
    Updates the fraud pattern by hour graph based on the provided application state data.

    This function processes transactional data to extract information about fraudulent
    transactions, groups the data by hour, and generates a figure combining a bar chart
    for the number of fraud cases and a line chart for the total fraud amount. The x-axis
    represents the hours of the day, while the y-axis includes dual axes: number of fraud
    cases on the left and the total fraud amount on the right.

    Args:
        _: The application state data, typically passed in as JSON serialized data from the
            application state store.

    Returns:
        plotly.graph_objects.Figure: A figure object representing the fraud pattern by hour,
            containing both a bar and a line chart.
    """
    dm = DataManager.get_instance()
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
        marker_color="#636EFA",
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
        title="Fraud by Hour: Number of Cases (Bar) & Total Amount (Line)",
        xaxis_title="Hour of Day",
        yaxis=dict(title="Number of Fraud Cases", side="left"),
        yaxis2=dict(title="Total Fraud Amount ($)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99)
    )
    return fig

# --- Patterns: Fraud by Weekday (Bar & Line) ---
@callback(
    Output(ID.FRAUD_PATTERN_WEEKDAY_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_weekday(_):
    """
    Generates and returns a Plotly figure representing fraud data distributed by weekday. The figure
    includes a bar graph for the number of fraud cases and a line graph for the total fraud amount.

    Args:
        _ (dict): Placeholder for Dash input callback data. The data from Input(ID.APP_STATE_STORE, "data")
            is not used directly in this function.

    Returns:
        plotly.graph_objects.Figure: A figure visualizing fraud data by weekday, including the total
        number of fraud cases per day, the total fraud amount, and the average fraud cost per case.
    """
    dm = DataManager.get_instance()
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
        marker_color="#636EFA",
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
        title="Fraud by Weekday: Number of Cases (Bar) & Total Amount (Line)",
        xaxis_title="Weekday",
        yaxis=dict(title="Number of Fraud Cases", side="left"),
        yaxis2=dict(title="Total Fraud Amount ($)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99)
    )
    return fig

# --- Patterns: Fraud Transaction Amounts (Box Plot) ---
@callback(
    Output(ID.FRAUD_PATTERN_AMOUNT_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_amount(_):
    """
    Updates and provides a box plot visualization of fraud transaction amounts.

    This callback function retrieves transaction data from the DataManager instance,
    filters transactions marked with errors (non-null and non-empty), and generates
    a box plot using Plotly to display the distribution of fraud transaction amounts.
    The resulting figure is updated in the specified output target.

    Args:
        _: Any
            Unused input data, often related to the application state.

    Returns:
        plotly.graph_objs._figure.Figure:
            A Plotly figure object representing a box plot of fraud transaction amounts.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    fig = px.box(df_fraud, y="amount", points="all", title="Fraud Transaction Amounts (Box Plot)")
    fig.update_layout(yaxis_title="Fraud Transaction Amount ($)")
    return fig

# --- Cards & Merchants: Fraud by Card Type (Bar) ---
@callback(
    Output(ID.FRAUD_CARD_TYPE_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_type(_):
    """
    Updates the fraud by card type bar chart figure for a given application state.

    This callback function generates a bar chart showing the number of fraud cases
    grouped by card type. The visualization also includes the total fraud amount
    and the number of cases per card type as textual annotations. The data is
    retrieved and processed from a central data manager to filter and aggregate
    fraudulent transactions by card type.

    Args:
        _: dict | None: The application state data, typically used as a trigger
            for the callback. Its details are not utilized in this function.

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly bar chart visualizing the fraud
        cases grouped by card type, with respective fraud amount annotations.

    """
    dm = DataManager.get_instance()
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
        labels={"x": "Card Type", "y": "Number of Fraud Cases"},
        title=f"Fraud by Card Type (Bar Chart)<br><sup>Total Fraud Amount: ${total_amount:,.2f}</sup>",
        text=bar_text
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="Card Type",
        yaxis_title="Number of Fraud Cases"
    )
    return fig

# --- Cards & Merchants: Fraud by Card Brand (Pie Chart) ---
@callback(
    Output(ID.FRAUD_CARD_BRAND_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_card_brand(_):
    """
    Callback that updates the "Fraud by Card Brand" pie chart based on the application state
    data. Processes transaction and card data to generate a figure visualization for the
    distribution of fraudulent transactions categorized by card brand.

    Args:
        _: Input value representing application state data.

    Returns:
        plotly.graph_objs.Figure: A pie chart figure representing the count of fraudulent
        transactions for each card brand.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    cards = dm.df_cards
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    merged = df_fraud.merge(cards, left_on="card_id", right_on="id", how="left")
    brand_counts = merged["card_brand"].value_counts()
    fig = px.pie(
        names=brand_counts.index,
        values=brand_counts.values,
        title="Fraud by Card Brand (Pie Chart)"
    )
    fig.update_traces(textinfo='label+value')
    fig.update_layout(legend_title="Card Brand")
    return fig

# --- Cards & Merchants: Top 10 Merchant Categories by Fraud Amount (Bar & Line) ---
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
    """
    Retrieves the name of a Merchant Category Code (MCC) from a mapping.

    The function takes an MCC code as input, converts it to a string, and looks it up
    in a provided mapping to determine the corresponding MCC name. If the MCC code
    does not exist in the mapping, a string indicating "Unknown" along with the MCC
    code is returned.

    Args:
        mcc_code: The Merchant Category Code (MCC) to look up.
        mcc_map: A dictionary mapping MCC codes (as strings) to their corresponding
            names.

    Returns:
        A string representing the name of the MCC if found in the mapping. If not
        found, a string in the format "Unknown (MCC_CODE)" is returned, where
        MCC_CODE is the input code converted to a string.
    """
    code_str = str(mcc_code)
    return mcc_map.get(code_str, f"Unknown ({code_str})")

@callback(
    Output(ID.FRAUD_MCC_GRAPH, "figure"),
    Input(ID.APP_STATE_STORE, "data"),
)
def update_fraud_by_mcc(_):
    """
    Updates a line graph visualizing the top 10 merchant categories by fraud costs.

    This callback function generates a line chart that represents the total fraud
    amount associated with the top 10 merchant categories by fraud costs. Fraudulent
    transactions are identified based on non-empty values in the "errors" column
    of the transaction data. It calculates the total fraud amount, the number of
    cases, and the average fraud amount per category. The function filters out the
    relevant data, performs necessary aggregations, sorts the categories by total
    costs in descending order, and maps merchant category codes (MCC) to their
    respective names. Finally, a line chart is constructed using Plotly express.

    Args:
        _: Any: Triggering input data (not used explicitly in this function).

    Returns:
        go.Figure: A Plotly line chart figure representing the top 10 merchant
            categories by total fraud costs, with markers for data points.
    """
    dm = DataManager.get_instance()
    df = dm.df_transactions
    df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
    if "mcc" not in df_fraud.columns or df_fraud.empty:
        return go.Figure()
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
        title="Top 10 Merchant Categories by Total Fraud Amount (Line Chart)",
        labels={"x": "Merchant Category", "costs": "Total Fraud Amount ($)"}
    )
    fig.update_traces(mode="lines+markers", marker_color="#EF553B")
    return fig

