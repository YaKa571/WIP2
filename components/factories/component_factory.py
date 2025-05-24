import json
import time
import urllib.request

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import us
from dash import dash_table, html, dcc
from plotly.graph_objs._figure import Figure
from shapely.geometry import shape

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


def create_usa_map(color_scale: str = "Blues",
                   map_style: str = "carto-positron-nolabels") -> dcc.Graph:
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
    Returns
    -------
    dash_core_components.Graph
        A Dash Graph component representing the map.
    """
    state_counts = (
        dm.df_transactions
        .dropna(subset=["state_name"])
        .groupby("state_name", as_index=False)
        .size()
        .rename(columns={"size": "transaction_count"})
    )

    # Choropleth Mapbox
    fig = px.choropleth_map(
        state_counts,
        geojson=states_geo,
        locations="state_name",
        featureidkey="properties.name",
        color="transaction_count",
        color_continuous_scale=color_scale,
        labels={"transaction_count": "Transactions"},
        map_style=map_style
    )

    # Text with state abbreviations
    fig.add_trace(go.Scattermap(
        lat=[state_centroids[n][0] for n in state_counts["state_name"]],
        lon=[state_centroids[n][1] for n in state_counts["state_name"]],
        mode="text",
        text=[full_to_abbr[n] for n in state_counts["state_name"]],
        textfont=dict(size=12, color="black"),
        showlegend=False,
        hoverinfo="skip"
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
        uirevision=str(time.time()),
    )

    # Remove color scale
    fig.update_coloraxes(showscale=False)

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
                "Open Settings",
                html.Br(),
                "Shortcut: S"
            ],
                target=ID.BUTTON_SETTINGS_MENU.value,
                placement="bottom-start",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "settings-button"},
            ),
            dbc.Tooltip(children=[
                "Toggle Theme",
                html.Br(),
                "Shortcut: T"
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
        title: str,
        graph_id: str,
        figure: Figure = None,
        config: dict = None
) -> dbc.Card:
    """
    Creates a card component that contains a circular diagram graph with a header.

    This function constructs a Dash Bootstrap Card component to display a circular
    diagram graph. It includes a customizable icon and title in the header, and
    renders a Dash Core Component (dcc.Graph) in the card body. A user can specify
    the graph data, its configuration, and other parameters through the function
    arguments.

    Args:
        icon_id (IconID): The ID of the icon to be displayed in the card header.
        title (str): The title for the card header.
        graph_id (str): The unique identifier for the graph component.
        figure (Figure, optional): The figure object containing data for the
            circular diagram. Defaults to an empty Figure instance.
        config (dict, optional): Configuration dictionary for the graph. If not
            provided, a default configuration (PIE_CONFIG) will be used.

    Returns:
        dbc.Card: A Dash Bootstrap card component containing the circular diagram
            graph with the specified header and configuration.
    """
    return dbc.Card(
        className="graph-card",
        children=[

            dbc.CardHeader(
                children=[

                    create_icon(icon_id, cls="icon icon-small"),
                    html.P(children=title, className="graph-card-title")

                ]),

            dbc.CardBody(
                children=[

                    dcc.Graph(
                        figure=figure or Figure(),
                        className="circle-diagram",
                        id=graph_id,
                        responsive=True,
                        config=config or CIRCLE_DIAGRAM_CONFIG,
                        style={"height": "100%"}
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
        dark_mode: bool = False,
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
    text_color = "white" if dark_mode else "black"
    transparent_color = "rgba(0,0,0,0)"
    grid_color = "rgba(230,230,230,100)" if dark_mode else "rgba(25,25,25,100)"

    px_bar_kwargs = dict(
        data_frame=df,
        x=x,
        y=y,
        hover_data=hover_data,
        color=color,
        color_discrete_map=color_discrete_map,
        labels=labels
    )

    if title:
        px_bar_kwargs["title"] = title

    if custom_data:
        px_bar_kwargs["custom_data"] = custom_data

    fig = px.bar(**px_bar_kwargs)

    fig.update_xaxes(type="category", categoryorder=x_category_order,
                     linecolor=grid_color, gridcolor=transparent_color)

    fig.update_yaxes(showline=False, linecolor=grid_color, gridcolor=grid_color)

    if bar_color and not color:
        fig.update_traces(marker_color=bar_color)

    fig.update_traces(marker_line_width=0,
                      opacity=0.95)

    if hover_template:
        fig.update_traces(hovertemplate=hover_template)

    fig.update_layout(
        paper_bgcolor=transparent_color,
        plot_bgcolor=transparent_color,
        margin=margin or dict(l=32, r=32, t=32, b=32),
        title_x=0.5,
        title_y=0.975,
        showlegend=showlegend,
        modebar={"orientation": "h"},
        font=dict(color=text_color),
        xaxis=dict(title_font=dict(color=text_color), tickfont=dict(color=text_color)),
        yaxis=dict(title_font=dict(color=text_color), tickfont=dict(color=text_color)),
        legend=dict(font=dict(color=text_color),
                    x=1.00275, xanchor="right", y=1.04, yanchor="top",
                    orientation="h"),
        title=dict(font=dict(color=text_color)),
        barcornerradius="16%"
    )

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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig
