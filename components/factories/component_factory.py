import json
import time
import urllib.request
from typing import Union

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import us
from dash import dash_table, html, dcc
from plotly.graph_objs._figure import Figure
from shapely.geometry import shape

import components.constants as const
from backend.data_manager import DataManager
from frontend.component_ids import ID
from frontend.icon_manager import IconID, Icons

dm: DataManager = DataManager.get_instance()

# Config for pie graphs
CIRCLE_DIAGRAM_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False
}

# GLOBAL DICT that holds all DataFrames
DATASETS: dict[str, pd.DataFrame] = {}

# -> Load GeoJSON of US states (only once at app startup)
with urllib.request.urlopen(
        "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
) as response:
    states_geo = json.load(response)

online_polygon = {
    "type": "Feature",
    "properties": {"name": "ONLINE"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [dm.online_shape]
    }
}
states_geo["features"].append(online_polygon)

# Calculate centroids (lon, lat) and mapping full-name -> abbreviation
state_centroids = {}
full_to_abbr = {}
for feat in states_geo["features"]:
    name = feat["properties"]["name"]
    geom = shape(feat["geometry"])
    lon, lat = geom.centroid.coords[0]
    state_centroids[name] = (lat, lon)
full_to_abbr = {s.name: s.abbr for s in us.states.STATES}


def create_data_table(id_name: str, dataset: pd.DataFrame, visible: bool = True, page_size: int = 10) -> dbc.Card:
    """
    Creates a data table wrapped inside a Dash Bootstrap Card component.

    This function generates a Dash DataTable using the provided dataset and wraps
    it in a styled Dash Bootstrap Card component. The DataTable includes pagination
    support.The card's visibility can be toggled using a boolean parameter.

    :param id_name: A unique identifier for the DataTable component.
    :param dataset: A pandas DataFrame containing the data to be displayed in the
        DataTable. It will be converted to a dictionary structure suitable for Dash.
    :type dataset: pd.DataFrame
    :param visible: A boolean flag to indicate whether the card (and the table
        within it) should be visible or hidden. Defaults to True.
    :type visible: bool
    :param page_size: Number of data records to display per table page.
    :return: A Dash Bootstrap Card containing the styled DataTable component.
    :rtype: dbc.Card
    """
    # Save Dataset
    DATASETS[id_name] = dataset

    # Column definition
    columns = [{"name": col, "id": col} for col in dataset.columns]

    # Return card with DataTable
    return dbc.Card(
        dbc.CardBody(
            [
                html.H3(str.upper(id_name), className="card-title"),

                # Wrap DataTable in a Div with our custom CSS style
                html.Div(
                    dash_table.DataTable(
                        id={"type": "data-table", "index": id_name},
                        columns=columns,
                        data=[],  # Initially empty
                        page_current=0,
                        page_size=page_size,
                        page_action="custom",  # <-- Server-side paging
                        cell_selectable=False,
                        virtualization=False
                    ),
                    className="datatable"
                )
            ]
        ),
        className="mb-3 card",
        style={"display": "block"} if visible else {"display": "none"}
    )


def create_usa_map(color_scale: str = const.MAP_DEFAULT_COLOR_SCALE,
                   map_style: str = "carto-positron-nolabels",
                   text_color: str = "black" if const.DEFAULT_DARK_MODE else "white",
                   dark_mode: bool = const.DEFAULT_DARK_MODE,
                   show_color_scale: bool = True) -> dcc.Graph:
    """
    Creates a choropleth map of the United States illustrating transaction count
    per state. The map is built using Plotly Map and shows states colored by
    transaction density on a red color scale. State abbreviations are overlaid as
    text annotations.

    Parameters
    ----------
    color_scale : str, optional
        The graphs color scale to use, by default "Reds"
    map_style: str, optional
        Mapbox style to use, by default "carto-positron"
    text_color: str, optional
        The color to use for text, by default "black"
    dark_mode: bool, optional
        Whether to use dark mode colors, by default True
    show_color_scale: bool, optional
        Whether to show the color scale on the map, by default True
    Returns
    -------
    dash_core_components.Graph
        A Dash Graph component representing the map.
    """
    df = dm.home_tab_data.map_data
    text_color_colorbar = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    text_font = "Open Sans Bold, Open Sans, Arial, sans-serif"

    # Choropleth Mapbox
    fig = px.choropleth_map(
        df,
        geojson=states_geo,
        locations="state_name",
        featureidkey="properties.name",
        color="transaction_count",
        color_continuous_scale=color_scale,
        labels={"transaction_count": "Transactions"},
        map_style=map_style,
        custom_data=["state_name_upper"]
    )

    # Add hover template
    fig.update_traces(
        hovertemplate="<b>📍 STATE:</b> %{customdata[0]}<br><b>💳 TRANSACTIONS:</b> %{z:,}<extra></extra>"
    )

    # Text with state abbreviations
    fig.add_trace(go.Scattermap(
        lat=[state_centroids[n][0] for n in df["state_name"]],
        lon=[state_centroids[n][1] for n in df["state_name"]],
        mode="text",
        text=[full_to_abbr.get(n, "ONLINE") if n != "ONLINE" else "ONLINE"
              for n in df["state_name"]],
        textfont=dict(size=12, color=text_color, family=text_font),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Update layout
    fig.update_layout(
        autosize=False,
        map=dict(
            center={"lat": 37.8, "lon": -96.9},
            zoom=3,
        ),
        margin=dict(
            b=0,
            l=0,
            r=0,
            t=0,
        ),
        uirevision="usa-map",
    )

    fig.update_coloraxes(
        colorbar=dict(
            title="TRANSACTIONS",
            orientation='h',
            x=0.5,
            y=0.05,
            xanchor='center',
            yanchor='bottom',
            len=0.7,
            thickness=20,
            tickfont=dict(color=text_color_colorbar, family=text_font),
            title_font=dict(color=text_color_colorbar, family=text_font),
        ),
        showscale=show_color_scale
    )

    return dcc.Graph(
        id=ID.MAP.value,
        figure=fig,
        config={"displayModeBar": False, "scrollZoom": True},
        className="map",
        style={"height": "100%", "width": "100%"},
        responsive=True
    )


def create_tooltips():
    """
    Creates a container that holds tooltip components designed to provide additional
    contextual information or shortcuts for the specified targets. Each tooltip is
    associated with a unique target and can be triggered by hover. The placement of
    the tooltip specifies the alignment of the tooltip relative to its target.

    Returns:
        html.Div: A div element containing the configured tooltip components.

    """
    return html.Div(
        children=[

            dbc.Tooltip(children=[
                "OPEN SETTINGS",
                html.Hr(),
                "SHORTCUT: S"
            ],
                target=ID.BUTTON_SETTINGS_MENU.value,
                placement="bottom-start",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "settings-button"},
            ),
            dbc.Tooltip(children=[
                "TOGGLE THEME",
                html.Hr(),
                "SHORTCUT: T"
            ],
                target=ID.BUTTON_DARK_MODE_TOGGLE.value,
                placement="bottom-end",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "dark-mode-toggle"},
            ),
            # Add more...

        ],
        style={"display": "contents"}
    )


def create_icon(icon_id: IconID, cls: str = "icon") -> html.Img:
    """
    Creates an HTML image element representing an icon. This function generates
    an image element using the specified icon identifier and allows customization
    of the CSS class applied to the image. The created icon is not draggable.

    Parameters:
    icon_id: IconID
        The identifier of the icon to be used.
    cls: str, optional
        The CSS class name(s) to be applied to the image element. Default is "icon".

    Returns:
    html.Img
        The HTML image element representing the specified icon.
    """
    return html.Img(src=Icons.get_icon(icon_id), className=cls, draggable="False")


def create_info_icon(icon_id: ID, style: dict = None) -> html.I:
    """
    Creates an HTML info icon element with the specified ID.

    This function generates an HTML <i> tag meant to represent an info icon. It applies
    specific classes to style the icon as a "bi bi-info-circle-fill info-icon" and assigns
    the provided ID to the element.

    Parameters:
    id (ID): The unique identifier to be assigned to the HTML info icon element.

    Returns:
    html.I: HTML <i> element with specified id and predefined classes.
    """
    return html.I(className="bi bi-info-circle-fill info-icon", id=icon_id, style=style)


def create_circle_diagram_card(
        icon_id: IconID,
        title: Union[str, list],
        graph_id: str,
        figure: Figure = None,
        config: dict = None
) -> dbc.Card:
    """
    Creates a Dash Bootstrap Components card element containing a circle diagram graph.
    This function generates a card layout with a header displaying an icon and title,
    and a body containing a graph. The graph's figure and configuration can be customized.

    Args:
        icon_id (IconID): ID of the icon to be displayed in the card header.
        title (str): Title of the card. If it contains " by ", the text following this
            phrase will be placed on a separate line.
        graph_id (str): ID to assign to the graph for interactivity and identification
            within the Dash application.
        figure (Figure, optional): A Plotly Figure object to be used as the graph's
            data and layout. Defaults to None, in which case an empty Figure object
            is used.
        config (dict, optional): Configuration options for the graph. If not provided,
            defaults to a predefined CIRCLE_DIAGRAM_CONFIG setting.

    Returns:
        dbc.Card: A Dash Bootstrap Components card element containing the specified
        icon, title, and circle diagram graph.
    """

    if isinstance(title, list):
        title_children = []
        for idx, part in enumerate(title):
            title_children.append(part)
            if idx < len(title) - 1:
                title_children.append(html.Br())
    else:
        title_children = [title]

    return dbc.Card(
        className="graph-card",
        children=[

            dbc.CardHeader(
                children=[

                    create_icon(icon_id, cls="icon icon-small"),
                    html.P(children=title_children, className="graph-card-title")

                ]),

            dbc.CardBody(
                children=[

                    dcc.Graph(
                        figure=figure or create_empty_figure(),
                        className="circle-diagram",
                        id=graph_id,
                        responsive=True,
                        config=config or CIRCLE_DIAGRAM_CONFIG,
                        style={"height": "100%", "width": "100%"},
                    )

                ])
        ])


def create_kpi_card(icon_id: IconID, title: str, div_id: str) -> dbc.Card:
    """
    Creates a KPI (Key Performance Indicator) card component.

    This function generates a customizable KPI card designed for displaying key
    metrics or indicators. The card includes an icon, title, and a space to
    display dynamic values. It allows for designation of an HTML division ID to
    enable targeted modifications or updates to the card's content.

    Parameters:
    icon_id (IconID): The identifier for the icon to be displayed in the card
                      header. Determines the visual representation of the icon.
    title (str): The title text to be displayed on the card's header.
    div_id (str): The HTML ID of the division containing the dynamic contents of
                  the card's body.

    Returns:
    dbc.Card: A Dash Bootstrap component representing the KPI card with the
              specified attributes and layout.
    """
    return dbc.Card(
        className="kpi-card",
        children=[

            dbc.CardHeader(
                children=[

                    create_icon(icon_id, cls="icon icon-small"),
                    html.P(title, className="kpi-card-title"),

                ]),

            dbc.CardBody(
                children=[

                    html.Div(
                        id=div_id,
                        children=[

                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")

                        ])
                ])
        ])


def create_bar_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = None,
        hover_data: list = None,
        custom_data: list = None,
        hover_template: str = None,
        color: str = None,
        color_discrete_map: dict = None,
        labels: dict = None,
        x_category_order: str = "total descending",
        bar_color: str = None,
        margin: dict = None,
        showlegend: bool = False,
        num_visible_bars: int = 10,
        dark_mode: bool = const.DEFAULT_DARK_MODE,
) -> go.Figure:
    """
    Creates a bar chart visualization using Plotly.

    This function generates a bar chart based on the provided DataFrame and configuration
    parameters. It allows customization of the x and y axes, hover data, colors, labels,
    category ordering, and layout settings. The function returns a Plotly Figure object
    representing the bar chart.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to be plotted.
    x : str
        The column name in the DataFrame to be used for the x-axis.
    y : str
        The column name in the DataFrame to be used for the y-axis.
    title : str
        The title of the bar chart.
    hover_data : list, optional
        A list of column names from the DataFrame to display as additional information
        when hovering over a bar.
    color : str, optional
        The column name in the DataFrame to be used for the color grouping.
    color_discrete_map : dict, optional
        A dictionary mapping data values to specific colors for the bars.
    labels : dict, optional
        A dictionary mapping column names or axis titles to custom labels.
    x_category_order : str, optional
        The order in which categories should appear on the x-axis. Defaults
        to "total descending".
    bar_color : str, optional
        The color to apply to all bars if no `color` parameter is specified.
    margin : dict, optional
        A dictionary specifying the margins of the plot, with keys "l", "r", "t", and "b"
        for left, right, top, and bottom margins, respectively.
    showlegend : bool, optional
        Whether to display the legend on the chart. Defaults to False.

    Returns
    -------
    go.Figure
        A Plotly Figure object representing the bar chart.
    """

    # Extract constants
    DEFAULT_MARGIN = dict(l=32, r=32, t=32, b=32)
    DEFAULT_OPACITY = 0.95
    DEFAULT_MARKER_LINE_WIDTH = 0

    # Set theme colors
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    # Build base configuration
    chart_config = {
        "data_frame": df,
        "x": x,
        "y": y
    }

    # Add optional parameters
    optional_params = {
        "hover_data": hover_data,
        "color": color,
        "color_discrete_map": color_discrete_map,
        "labels": labels,
        "title": title,
        "custom_data": custom_data
    }
    chart_config.update({k: v for k, v in optional_params.items() if v is not None})

    # Create figure
    fig = px.bar(**chart_config)

    def update_axes_style():
        """
        Creates a bar chart visualization based on the provided parameters and data. The function generates
        a Plotly bar chart figure using the input dataframe and various customizable options, such as axis
        labels, colors, hover data, and chart title. This function supports additional configurations like
        customizing hover templates, ordering of categories on the x-axis, and enabling a dark mode theme.

        Args:
            df (pd.DataFrame): The data source to be visualized in the bar chart.
            x (str): The column name to be used for the x-axis.
            y (str): The column name to be used for the y-axis.
            title (str, optional): The title of the bar chart. Defaults to None.
            hover_data (list, optional): A list of additional column names to display on hover. Defaults to None.
            custom_data (list, optional): A list of custom data fields for use in hover templates. Defaults to None.
            hover_template (str, optional): A custom hover template string for the bar chart. Defaults to None.
            color (str, optional): The column name to use for bar coloring. Defaults to None.
            color_discrete_map (dict, optional): A dictionary mapping discrete color categories to specific values. Defaults to None.
            labels (dict, optional): A mapping of axis or legend labels to more readable names. Defaults to None.
            x_category_order (str, optional): The order of x-axis categories, e.g., "total descending". Defaults to "total descending".
            bar_color (str, optional): Custom color for the bars in the chart. Applicable only if `color` is not set. Defaults to None.
            margin (dict, optional): A dictionary defining chart margins (layout.margin in Plotly). Defaults to None.
            showlegend (bool, optional): Whether to display the chart legend. Defaults to False.
            dark_mode (bool, optional): Whether to apply dark mode styling to the chart. Defaults to False.

        Returns:
            go.Figure: A Plotly figure object representing the constructed bar chart.

        """
        fig.update_xaxes(
            type="category",
            categoryorder=x_category_order,
            linecolor=grid_color,
            gridcolor=const.COLOR_TRANSPARENT,
            range=[-0.5, num_visible_bars - 0.5]
        )
        fig.update_yaxes(
            showline=False,
            linecolor=grid_color,
            gridcolor=grid_color,
            zeroline=True,
            zerolinecolor=grid_color
        )

    def update_trace_style():
        """
        Generates a bar chart using provided data and customization options.

        This function creates a bar chart using Plotly with extensive options for
        configuration, including axis data, titles, hover styles, color schemes,
        and layout customizations.

        Args:
            df (pd.DataFrame): The input DataFrame containing data for the bar chart.
            x (str): The column name in the DataFrame to be used for the x-axis.
            y (str): The column name in the DataFrame to be used for the y-axis.
            title (str, optional): The title of the bar chart. Defaults to None.
            hover_data (list, optional): A list of columns to be displayed in the hover
                tooltip. Defaults to None.
            custom_data (list, optional): A list of columns to enable custom data bindings.
                Defaults to None.
            hover_template (str, optional): A custom hover template to format tooltips.
                Defaults to None.
            color (str, optional): The column name in the DataFrame to be used for color
                encoding. Defaults to None.
            color_discrete_map (dict, optional): A dictionary defining the mapping of
                discrete color values. Defaults to None.
            labels (dict, optional): A dictionary to map column names to axis labels or
                legends. Defaults to None.
            x_category_order (str, optional): The order of categories on the x-axis
                ('total ascending', 'total descending', or 'trace'). Defaults to
                "total descending".
            bar_color (str, optional): A single color to be applied to all bars. Ignored
                if `color` is provided. Defaults to None.
            margin (dict, optional): A dictionary specifying the margins around the plot.
                Defaults to None.
            showlegend (bool, optional): If True, displays a legend. Defaults to False.
            dark_mode (bool, optional): If True, enables a dark mode theme for the chart.
                Defaults to False.

        Returns:
            go.Figure: The generated bar chart as a Plotly Figure object.

        Raises:
            KeyError: If the column names specified in x, y, or other arguments are not
                present in the DataFrame.

        Note:
            The `update_trace_style` inner function applies additional styling options
            to the chart traces, such as marker line width, opacity, and hover templates.
            If `bar_color` is specified and `color` is not provided, the bars are
            uniformly styled with `bar_color`.
        """
        trace_updates = {
            "marker_line_width": DEFAULT_MARKER_LINE_WIDTH,
            "opacity": DEFAULT_OPACITY
        }
        if bar_color and not color:
            trace_updates["marker_color"] = bar_color
        if hover_template:
            trace_updates["hovertemplate"] = hover_template
        fig.update_traces(**trace_updates)

    def update_chart_layout():
        """
        Creates a bar chart visualization using Plotly and applies customizable layout settings.

        This function generates a bar chart from the provided DataFrame, allowing for a high level of
        customization regarding aesthetics, annotations, hover information, colors, and layout properties.
        The chart's layout and color scheme can also be adapted for dark mode or other preferences.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            x (str): Column name in the DataFrame corresponding to the x-axis values.
            y (str): Column name in the DataFrame corresponding to the y-axis values.
            title (str, optional): Title for the chart.
            hover_data (list, optional): List of column names to include in hover data.
            custom_data (list, optional): List of column names for custom data bindings.
            hover_template (str, optional): Template string for formatting hover tooltips.
            color (str, optional): Column name for assigning colors to bars.
            color_discrete_map (dict, optional): A dictionary mapping values from the `color` column
                to discrete colors.
            labels (dict, optional): Mapping of column names to axis or legend labels.
            x_category_order (str, optional): Order of categories on the x-axis (default is "total descending").
            bar_color (str, optional): Color for the bars when a single color is desired.
            margin (dict, optional): Dictionary defining plot layout margins.
            showlegend (bool, optional): Whether to display the chart's legend.
            dark_mode (bool, optional): Whether to format the chart for dark mode.

        Returns:
            go.Figure: A Plotly Figure object representing the generated bar chart.
        """
        fig.update_layout(
            paper_bgcolor=const.COLOR_TRANSPARENT,
            plot_bgcolor=const.COLOR_TRANSPARENT,
            margin=margin or DEFAULT_MARGIN,
            title_x=0.5,
            title_y=0.975,
            showlegend=showlegend,
            modebar={"orientation": "h"},
            font=dict(color=text_color),
            xaxis=dict(title_font=dict(color=text_color), tickfont=dict(color=text_color)),
            yaxis=dict(title_font=dict(color=text_color), tickfont=dict(color=text_color)),
            legend=dict(
                font=dict(color=text_color),
                x=1.00275,
                xanchor="right",
                y=1.04,
                yanchor="top",
                orientation="h"
            ),
            title=dict(font=dict(color=text_color)),
            barcornerradius="16%"
        )

    # Apply styles
    update_axes_style()
    update_trace_style()
    update_chart_layout()

    return fig


def create_empty_figure():
    """
    Creates an empty Plotly figure with a transparent background, invisible axes, and
    minimal margins. This function is useful as a placeholder or for initializing a
    template figure with specific layout settings.

    Returns:
        go.Figure: A Plotly figure object with predefined layout settings.
    """
    fig = go.Figure()
    fig.update_layout(
        xaxis={'visible': False},
        yaxis={'visible': False},
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig
