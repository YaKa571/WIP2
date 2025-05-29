import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html

import components.constants as const
import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from components.constants import COLOR_BLUE_MAIN, COLOR_FEMALE_PINK
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()
home_data = dm.home_tab_data


def create_pie_graph(data: dict, colors=None, textinfo: str = "percent+label",
                     hover_template: str = None, showlegend: bool = True,
                     dark_mode: bool = False, center_text: str = None) -> go.Figure:
    """
    Create a pie graph visualization.

    This function generates a pie chart visualization using the given data.
    It allows customization of colors, text information display, legend visibility,
    and a dark mode for the chart appearance.

    Arguments:
        data: dict
            A dictionary containing labels as keys and corresponding values as values
            for the pie chart sections.
        colors: list, optional
            A list of colors for the pie slices. Defaults to ["#c65ed4", "#5d9cf8"].
        textinfo: str, optional
            String specifying which text elements to show on the chart (e.g., 'percent+label').
            Defaults to "percent+label".
        showlegend: bool, optional
            Determines whether to display the legend on the chart. Defaults to True.
        dark_mode: bool, optional
            Configures text color and background appearance for dark mode. Defaults to False.

    Returns:
        go.Figure
            A Plotly Figure object representing the pie chart visualization.
    """
    if colors is None:
        colors = [COLOR_FEMALE_PINK, COLOR_BLUE_MAIN]  # Female = pink, Male = blue

    textcolor = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT

    labels = list(data.keys())
    values = list(data.values())

    # Create pull values for single slices
    if len(values) > 2:
        pull = [0.1 if v == max(values) else 0 for v in values]
    else:
        pull = [0 for _ in values]

    fig = go.Figure(
        data=[
            go.Pie(
                name="",
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=colors),
                textinfo=textinfo,
                textfont=dict(color=textcolor),
                hovertemplate=hover_template,
                pull=pull,
            )
        ],
        layout=go.Layout(
            margin=dict(l=1, r=1, t=1, b=1),
            showlegend=showlegend
        )
    )

    fig.update_layout(
        paper_bgcolor=const.COLOR_TRANSPARENT,  # Transparent background
        plot_bgcolor=const.COLOR_TRANSPARENT,
        legend=dict(
            x=1,  # 100% right
            y=1,  # 100% top
            xanchor="right",
            yanchor="top",
            font=dict(size=12, color="#0d6efd", weight="bold")
        )
    )

    fig.add_annotation(
        text=center_text,
        showarrow=False,
        font=dict(size=15, color=textcolor, family="Open Sans"),
        x=0.5, y=0.5, xref="paper", yref="paper",
        xanchor="center", yanchor="middle"
    )

    fig.update_traces(textposition="inside",
                      texttemplate="<b>%{label}</b><br><span style='font-size:16px'>%{percent}</span>")

    return fig


def get_most_valuable_merchant_details(state: str = None) -> list:
    """
    Fetches and generates HTML components that display the most valuable merchant's
    details. The function retrieves the most profitable merchant's description and
    value for a given state, wraps them in HTML components, and returns them as
    elements in a list.

    Parameters:
        state (str, optional): The state for which the most valuable merchant's
        information should be retrieved. Defaults to None.

    Returns:
        list: A list containing two HTML components. The first component displays
        the merchant's description, and the second displays the monetary value
        associated with the merchant.

    """
    # Get merchant data once to avoid redundant calls
    merchant = dm.home_tab_data.get_most_valuable_merchant(state)

    one = html.P(
        f"{merchant.mcc_desc}",
        className="kpi-card-value")

    two = html.P(f"${merchant.value}",
                 className="kpi-card-value kpi-number-value")

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_1"},
        target=ID.HOME_KPI_MOST_VALUABLE_MERCHANT,
        children=[
            f"🆔 MERCHANT ID: {merchant.id}",
            html.Br(),
            f"🏷️ MCC: {merchant.mcc}"
        ])

    return [one, two, tooltip]


def get_most_visited_merchant_details(state: str = None) -> list:
    """
    Fetches and returns the details of the most visited merchant for a given state.

    The function retrieves details of the most visited merchant, such as the merchant's
    description and the number of visits, and formats them as HTML components.

    Parameters:
        state (str, optional): The state for which the most visited merchant's
        details are to be fetched. Defaults to None.

    Returns:
        list: A list containing two HTML components. The first component includes the
        description of the most visited merchant, and the second component includes
        the number of visits.
    """
    # Get merchant data once to avoid redundant calls
    merchant = home_data.get_most_visited_merchant(state)

    one = html.P(
        f"{merchant.mcc_desc}",
        className="kpi-card-value")

    two = html.P(f"{merchant.visits} visits",
                 className="kpi-card-value kpi-number-value")

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_2"},
        target=ID.HOME_KPI_MOST_VISITED_MERCHANT,
        children=[
            f"🆔 MERCHANT ID: {merchant.id}",
            html.Br(),
            f"🏷️MCC: {merchant.mcc}"
        ])

    return [one, two, tooltip]


def get_top_spending_user_details(state: str = None) -> list:
    """
    Retrieves details of the top spending user in a given state. This function fetches the
    top spending user's details, such as gender, age, and spending value, formats them
    into presentable components, and returns them as a list.

    Parameters:
    state: str, optional
        The state for which to retrieve the top spending user details. If not provided,
        data is fetched for all states.

    Returns:
    list
        A list of top spending user details, including formatted gender, age, and
        spending value.
    """
    # Get user data once to avoid redundant calls
    user = home_data.get_top_spending_user(state)

    one = html.P(
        f"{user.gender}, {user.current_age} years",
        className="kpi-card-value")

    two = html.P(f"${user.value}", className="kpi-card-value kpi-number-value")

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_3"},
        target=ID.HOME_KPI_TOP_SPENDING_USER,
        children=[
            f"🆔 USER ID: {user.id}"
        ])

    return [one, two, tooltip]


def get_peak_hour_details(state: str = None) -> list:
    """
    Fetches and returns the details of peak hour metrics for a given state. This includes
    the hour range during which peak activity occurs and the number of transactions
    recorded during that period. The function constructs HTML components containing
    these details for consistent rendering in the application.

    Args:
        state (str, optional): The state identifier for which peak hour details are
            requested. Defaults to None.

    Returns:
        list: A list of HTML paragraph elements containing the peak hour range and the
            transaction count information.
    """
    # Get peak hour data once to avoid redundant calls
    peak_hour = home_data.get_peak_hour(state)

    one = html.P(f"{peak_hour.hour_range}", className="kpi-card-value")
    two = html.P(f"{peak_hour.value} transactions", className="kpi-card-value kpi-number-value")

    return [one, two]


def get_most_valuable_merchant_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generates a bar chart to visualize the top 10 most valuable merchants based on their total
    transaction values for a given state or all states.

    This function retrieves the merchant transaction values, sorts them, and selects the top
    10 merchants. It then generates a bar chart displaying the Merchant Category Code (MCC)
    against the total transaction values. Additional information such as merchant descriptions
    and IDs is available as hover data. The chart's appearance can be customized for light or
    dark mode rendering.

    Parameters:
        state (str, optional): The state code for which the top merchants are to be analyzed. If not
                               specified, the analysis includes all states.
        dark_mode (bool, optional): Determines the visual style of the chart. If True, the chart
                                    is displayed in dark mode. Defaults to False.

    Returns:
        plotly.graph_objects.Figure: A bar chart displaying the top 10 most valuable merchants
                                      for the specified state, or across all states when no state
                                      is provided.
    """
    df = home_data.get_merchant_values_by_state(state=state).head(10)
    df = df.copy()
    df["mcc_desc"] = df["mcc_desc"].astype(str).str.upper()

    hover_template = (
        "🏷️ <b>MCC:</b> %{x}<br>"
        "📝 <b>DESCRIPTION:</b> %{customdata[0]}<br>"
        "🆔 <b>MERCHANT ID:</b> %{customdata[1]}<br>"
        "💰 <b>SUM:</b> $%{y:,.2f}<br>"
        "<extra></extra>"
    )

    title = (
        "MERCHANTS IN ALL STATES" if state is None
        else "ONLINE MERCHANTS" if state == "ONLINE"
        else f"MERCHANTS IN {state.upper()}"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="merchant_id",
        y="merchant_sum",
        custom_data=["mcc_desc", "merchant_id"],
        hover_template=hover_template,
        title=f"TOP 10 MOST VALUABLE {title}",
        labels={"merchant_id": "MERCHANT ID", "merchant_sum": "SUM"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )


def get_peak_hour_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generates a bar chart depicting the most active transaction hours.

    The function retrieves transaction data for each hour of the day, filters out
    hours with no transactions, and formats the data for visualization. A bar chart
    is produced to represent transaction counts across hourly intervals. The chart
    includes customizable hover templates and supports dark mode presentation. If
    a specific state is provided, the chart focuses on data corresponding to that
    state. Otherwise, the chart displays data across all states.

    Parameters:
        state (str, optional): The name of the state to filter data for. Defaults to None,
                               meaning data for all states is used.
        dark_mode (bool, optional): Flag to indicate if the bar chart should be configured
                                    for dark mode appearance. Defaults to False.

    Returns:
        Figure: A bar chart visualizing the transaction counts by hour of the day.
    """
    df = home_data.get_transaction_counts_by_hour(state=state)
    df = df[df["transaction_count"] > 0].copy()
    df["hour_range"] = df["hour"].apply(lambda h: f"{h:02d}:00 – {(h + 1) % 24:02d}:00")

    hover_template = (
        "⏰ <b>HOUR:</b> %{customdata[0]}<br>"
        "💳 <b>TRANSACTIONS:</b> %{customdata[1]:,}<br>"
        "<extra></extra>"
    )

    title = (
        "IN ALL STATES" if state is None
        else "ONLINE" if state == "ONLINE"
        else f"IN {state.upper()}"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="hour_range",
        y="transaction_count",
        custom_data=["hour_range", "transaction_count"],
        hover_template=hover_template,
        title=f"MOST ACTIVE HOURS {title}",
        labels={"hour_range": "HOUR RANGE", "transaction_count": "TRANSACTIONS"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )


def get_spending_by_user_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generate a bar chart visualizing the top 10 most spending users. Users can be filtered by state, and the chart
    supports dark mode styling.

    Arguments:
        state (str, optional): The state for which the top users should be filtered. If not provided, includes all states.
        dark_mode (bool, optional): Determines whether the bar chart should be rendered in dark mode. Defaults to False.

    Returns:
        Bar chart visualization showcasing the top 10 spending users, with data categorized by gender and additional
        hover information such as gender, age, and spending.
    """
    df = home_data.get_spending_by_user(state).head(10)
    df = df.merge(dm.df_users[["id", "gender", "current_age"]], left_on="client_id", right_on="id").drop(columns=["id"])
    df = df.copy()

    df["gender"] = df["gender"].astype(str).str.upper()
    color_discrete_map = {"FEMALE": COLOR_FEMALE_PINK, "MALE": COLOR_BLUE_MAIN}

    hover_template = (
        "🆔 <b>USER ID:</b> %{x}<br>"
        "🧑‍🤝‍🧑 <b>GENDER:</b> %{customdata[0]}<br>"
        "🎂 <b>AGE:</b> %{customdata[1]}<br>"
        "💸 <b>SPENDING:</b> $%{customdata[2]:,.2f}<br>"
        "<extra></extra>"
    )

    title = (
        "IN ALL STATES" if state is None
        else "ONLINE" if state == "ONLINE"
        else f"IN {state.upper()}"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="client_id",
        y="spending",
        color="gender",
        color_discrete_map=color_discrete_map,
        custom_data=["gender", "current_age", "spending"],
        hover_template=hover_template,
        title=f"TOP 10 MOST SPENDING USERS {title}",
        labels={"client_id": "USER ID", "spending": "TOTAL SPENDING", "gender": "GENDER", "current_age": "AGE"},
        showlegend=True,
        dark_mode=dark_mode
    )


def get_most_visited_merchants_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generates a bar chart visualization for the top 10 most visited merchants. The chart
    displays merchant IDs on the x-axis and the number of visits on the y-axis, with
    additional hover data for merchant category code (MCC) and description. The state
    can be optionally specified to filter data for a specific region.

    Args:
        state (str, optional): The state for which to filter the merchant data.
            If None, data from all states is used. Defaults to None.
        dark_mode (bool, optional): Determines the color scheme of the chart. If True,
            the chart will use a dark theme. Defaults to False.

    Returns:
        A bar chart representation of the top 10 most visited merchants based on the
        specified parameters.
    """
    df = home_data.get_visits_by_merchant(state).head(10)
    df = df.copy()
    df["mcc_desc"] = df["mcc_desc"].astype(str).str.upper()

    hover_template = (
        "🏷️ <b>MCC:</b> %{customdata[0]}<br>"
        "📝 <b>DESCRIPTION:</b> %{customdata[1]}<br>"
        "🆔 <b>MERCHANT ID:</b> %{x}<br>"
        "👣 <b>VISITS:</b> %{customdata[2]:,}<br>"
        "<extra></extra>"
    )

    title = (
        "MERCHANTS IN ALL STATES" if state is None
        else "ONLINE MERCHANTS" if state == "ONLINE"
        else f"MERCHANTS IN {state.upper()}"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="merchant_id",
        y="visits",
        custom_data=["mcc", "mcc_desc", "visits"],
        hover_template=hover_template,
        title=f"TOP 10 MOST VISITED {title}",
        labels={"merchant_id": "MERCHANT ID", "visits": "VISITS"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )


def build_center_text(leader, leader_color, diff, color_green, tie_label="TIE", value=None, percent=None, font_size=20,
                      value_font_size=16):
    """
    Constructs and returns a formatted HTML string for a leader and associated values.

    This function generates an HTML string based on the leader type, associated values,
    and additional formatting options. If a leader is not tied, it includes the leader's
    name with specific styling. Optionally, it can include the leader's value and percentage
    contribution. If a leader is tied, a specific label will be displayed instead.

    Parameters:
    leader: str
        The name of the leader to display.
    leader_color: str
        The color code for the leader's name styling.
    diff: float or None
        The difference value to display for the leader. Can be None if not applicable.
    color_green: str
        The color code utilized for highlighting the difference or value.
    tie_label: str, default "TIE"
        The label to display when there is a tie. Defaults to "TIE".
    value: float or None, optional
        The numeric value associated with the leader. Can be None if not applicable.
    percent: float or None, optional
        The percentage value associated with the leader. Can be None if not applicable.
    font_size: int, default 20
        The font size for displaying the leader's name.
    value_font_size: int, default 16
        The font size for displaying numeric values or percentages.

    Returns:
    str
        A formatted HTML string representing the styled leader, values, and optional tie label.

    Raises:
    None
    """
    # If it's a tie, return a simple tie label
    if leader == tie_label:
        return f"<span style='color:#aaa; font-size:20px; font-weight:bold'>{tie_label}</span>"

    # Create the leader span with styling
    leader_span = f"<span style='color:{leader_color}; font-size:{font_size}px; font-weight:bold'>{leader}</span><br>"

    # Create the value span with styling
    value_span = f"<span style='color:{color_green}; font-size:{value_font_size}px; font-weight:bold'>"

    # Add value if provided
    if value is not None:
        value_span += f"${value:,.0f}"
        # Add percent if provided
        if percent is not None:
            value_span += f" ({percent:.1f}%)"
        value_span += "</span>"
        return leader_span + value_span

    # If no value but diff is provided, show the diff
    if diff is not None:
        diff_span = f"<span style='color:{color_green}; font-size:{value_font_size}px; font-weight:bold'>+${diff:,.0f}</span>"
        return leader_span + diff_span

    # If neither value nor diff is provided, just return the leader
    return leader_span


def get_leader_info(values: dict, label_colors: dict, tie_label="TIE"):
    """
    Determines the leading category based on provided values and calculates the difference
    between the leading category and the next highest. It also returns the label color
    corresponding to the leading category or a tie label if values are tied.

    Arguments:
        values (dict): A dictionary where keys represent category labels and values
            represent corresponding numerical values.
        label_colors (dict): A dictionary mapping category labels to their respective
            color codes.
        tie_label (str, optional): The label to be used when a tie occurs or no values
            are present. Defaults to "TIE".

    Returns:
        tuple: A tuple containing:
            - str: The label of the leading category, or the tie label.
            - str: The color code corresponding to the leading category, or the default
              tie color ("#aaa").
            - int: The difference between the leading value and the second highest
              value, or 0 in case of a tie.
    """
    # Only return tie if both present and values equal
    items = list(values.items())
    if not items or all(v == 0 for _, v in items):
        # No data at all
        return tie_label, "#aaa", 0

    if len(items) == 1:
        # Only one category present: it's the winner!
        label, val = items[0]
        return label, label_colors.get(label, "#000"), val  # diff = val, since other is 0

    # Two categories
    (label1, val1), (label2, val2) = items[0], items[1]
    if val1 == val2:
        return tie_label, "#aaa", 0
    if val1 > val2:
        return label1, label_colors.get(label1, "#000"), val1 - val2
    else:
        return label2, label_colors.get(label2, "#000"), val2 - val1


def get_age_leader_info(age_sums: dict, age_colors: list):
    """
    Gets the leader information based on the age group distribution. The leader information includes the
    age group with the highest value, its associated color, the value, the percentage contribution to the
    total, and the sum of all age group values.

    Attributes:
        age_sums (dict): Dictionary mapping age groups to their respective numeric values.
        age_colors (list): List of colors corresponding to each age group by index.

    Args:
        age_sums (dict): A dictionary where keys are age group labels and values are their associated numbers.
        age_colors (list): A list of string color codes corresponding to the age groups.

    Returns:
        tuple: A tuple containing the following elements:
            - top_group (str): The age group with the highest value.
            - leader_color (str): The color associated with the leading age group.
            - top_value (int): The value of the leading age group.
            - percent (float): The percentage contribution of the leading age group to the total.
            - total (int): The total of all values in age_sums.
    """
    if not age_sums:
        return "-", "#aaa", 0, 0, 0
    age_labels = list(age_sums.keys())
    age_values = list(age_sums.values())
    top_group, top_value = max(age_sums.items(), key=lambda x: x[1])
    try:
        leader_idx = age_labels.index(top_group)
        leader_color = age_colors[leader_idx]
    except ValueError:
        leader_color = "#a29bfe"  # Fallback
    total = sum(age_values)
    percent = (top_value / total) * 100 if total > 0 else 0
    return top_group, leader_color, top_value, percent, total
