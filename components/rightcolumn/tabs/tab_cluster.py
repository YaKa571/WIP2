import dash_bootstrap_components as dbc
from dash import html, dcc
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID
from components.constants import COLOR_BLUE_MAIN

def create_cluster_content():
    """
    Generates the content layout for the cluster tab.

    This function assembles and returns the Div element comprising the components
    required to construct the cluster tab interface. The components are organized
    as a heading, control elements, and visualization section within the Div.

    Returns:
        html.Div: A Div element containing all the components of the cluster tab.
    """
    return html.Div(
        className="tab-content-inner cluster-tab",
        children=[
            # NEW
            #create_cluster_heading(),
            #create_cluster_control_merchant_group(),
            html.P("Cluster Tab wird neu aufgesetzt, Finger weg")
            # OLD
            #_create_heading(),
            #_create_cluster_controls(),
            #_create_cluster_visualization()

        ]
    )