import json
import urllib.request

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import us
from dash import dash_table, html, dcc
from shapely.geometry import shape

from backend.data_manager import DataManager
from frontend.component_ids import IDs
from frontend.styles import STYLES, Style

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
                html.H3(str.upper(id_name), className="card-title text-center"),
                dash_table.DataTable(
                    id={"type": "data-table", "index": id_name},  # <-- Pattern-ID
                    columns=columns,
                    data=[],  # initially empty
                    page_current=0,
                    page_size=page_size,
                    page_action="custom",  # <-- server-side paging
                    style_table=STYLES[Style.TABLE],
                    style_header=STYLES[Style.TABLE_HEADER],
                    style_cell=STYLES[Style.TABLE_CELL],
                    style_data_conditional=STYLES[Style.TABLE_CONDITIONAL],
                    style_data=STYLES[Style.TABLE_DATA],
                    virtualization=False
                )
            ]
        ),
        className="mb-3 card",
        style={"display": "block"} if visible else {"display": "none"}
    )


def create_usa_map(data_manager: DataManager) -> dcc.Graph:
    """
    Creates a choropleth map of the United States illustrating transaction count
    per state. The map is built using Plotly Mapbox and shows states colored by
    transaction density on a red color scale. State abbreviations are overlaid as
    text annotations.

    Parameters
    ----------
    data_manager : DataManager
        An instance of the DataManager class containing the transaction data
        required for generating the map.

    Returns
    -------
    dash_core_components.Graph
        A Dash Graph component representing the map.
    """
    state_counts = (
        data_manager.df_transactions
        .dropna(subset=["state_name"])
        .groupby("state_name", as_index=False)
        .size()
        .rename(columns={"size": "transaction_count"})
    )

    # Choropleth Mapbox
    fig = px.choropleth_mapbox(
        state_counts,
        geojson=states_geo,
        locations="state_name",
        featureidkey="properties.name",
        color="transaction_count",
        color_continuous_scale="Reds",
        labels={"transaction_count": "Transactions"},
    )

    # Text with state abbreviations
    fig.add_trace(go.Scattermapbox(
        lat=[state_centroids[n][0] for n in state_counts["state_name"]],
        lon=[state_centroids[n][1] for n in state_counts["state_name"]],
        mode="text",
        text=[full_to_abbr[n] for n in state_counts["state_name"]],
        textfont=dict(size=12, color="black"),
        showlegend=False,
        hoverinfo="none"
    ))

    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center={"lat": 37.8, "lon": -96.9},
            zoom=3,
        ),
        margin={"l": 0, "r": 0, "t": 0, "b": 0})

    # Remove color scale
    fig.update_coloraxes(showscale=False)

    return dcc.Graph(
        id=str(IDs.MAP.value),
        figure=fig,
        responsive=True,
        config={"displayModeBar": False, "scrollZoom": True},
        className="map"
    )
