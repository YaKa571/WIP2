import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table

from frontend.styles import STYLES, Style


def create_data_table(dataset: pd.DataFrame, visible: bool = True, page_size: int = 10) -> dbc.Card:
    """
    Creates a data table wrapped inside a Dash Bootstrap Card component.

    This function generates a Dash DataTable using the provided dataset and wraps
    it in a styled Dash Bootstrap Card component. The DataTable includes pagination
    support.The card's visibility can be toggled using a boolean parameter.

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
    return dbc.Card(
        dbc.CardBody(
            dash_table.DataTable(
                id="table",
                data=dataset.to_dict("records"),
                page_size=page_size,
                page_current=0,
                style_table=STYLES[Style.TABLE],
                style_header=STYLES[Style.TABLE_HEADER],
                style_cell=STYLES[Style.TABLE_CELL],
                style_data_conditional=STYLES[Style.TABLE_CONDITIONAL],
                style_data=STYLES[Style.TABLE_DATA]
            )

        ), className="mb-3", style=STYLES[Style.CARD] if visible else STYLES[Style.CARD] | {"display": "none"}
    )
