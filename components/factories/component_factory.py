import json
import time
import urllib.request

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import us
from dash import dash_table, html, dcc
from shapely.geometry import shape

from backend.data_manager import DataManager
from frontend.component_ids import ID
from frontend.icon_manager import IconID, Icons

dm: DataManager = DataManager.get_instance()

# GLOBAL DICT that holds all DataFrames
DATASETS: dict[str, pd.DataFrame] = {}

# → Load GeoJSON of US states (only once at app startup)
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


# TODO: @Diego: Make KPI Tooltips update dynamically
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
            dbc.Tooltip(children=[
                f"Merchant ID: {dm.get_most_valuable_merchant().id}",
                html.Br(),
                f"MCC: {dm.get_most_valuable_merchant().mcc}"
            ],
                placement="bottom",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "tab_home_kpi_1"},
                target=ID.HOME_KPI_MOST_VALUABLE_MERCHANT
            ),
            dbc.Tooltip(children=[
                f"Merchant ID: {dm.get_most_visited_merchant().id}",
                html.Br(),
                f"MCC: {dm.get_most_visited_merchant().mcc}"
            ],
                placement="bottom",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "tab_home_kpi_2"},
                target=ID.HOME_KPI_MOST_VISITED_MERCHANT
            ),
            dbc.Tooltip(children=[
                f"User ID: {dm.get_top_spending_user().id}"
            ],
                placement="bottom",
                is_open=False,
                trigger="hover",
                id={"type": "tooltip", "id": "tab_home_kpi_3"},
                target=ID.HOME_KPI_TOP_SPENDING_USER
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
