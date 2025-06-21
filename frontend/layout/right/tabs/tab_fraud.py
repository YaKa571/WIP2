import dash_bootstrap_components as dbc
from dash import dcc, html

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID


def create_fraud_content():
    """
    Creates the content layout for the fraud tab in the application.

    This function generates and returns the main layout encapsulating a heading,
    KPI cards, and analysis tabs specific to the fraud section of the application.
    It structures the content using Dash's `html.Div` element.

    Returns:
        html.Div: A Dash HTML Div element containing the fraud tab's content layout.
    """
    return html.Div(
        children=[
            _create_heading(),
            _create_kpi_cards(),
            _create_analysis_tabs(),
        ],
        className="tab-content-inner fraud-tab"
    )


def _create_heading() -> html.Div:
    """
    Creates the heading component for the Fraud Overview tab.

    The heading component includes a placeholder paragraph, a heading element with
    specific styles and identifier, an information icon, and a tooltip that provides
    additional details about the Fraud Overview functionality.

    Returns:
        html.Div: A Dash HTML Div component that contains the heading of the Fraud
        Overview tab, along with related styled elements.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            html.P(),  # Placeholder
            html.H4("Fraud Overview", id=ID.FRAUD_TAB_HEADING, className="green-heading"),
            comp_factory.create_info_icon(ID.FRAUD_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.FRAUD_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "This tab shows potentially fraudulent activity, trends,",
                    html.Br(),
                    "and visualizations based on transaction and card data.",
                ],
            ),
        ]
    )


def _create_kpi_cards() -> html.Div:
    """
    Creates KPI cards for a dashboard interface.

    This function generates a flex-wrapper division containing KPI cards. Each card
    includes a title, an icon identifier, and a division identifier for visual
    representation and interactivity. The cards are dynamically created using the
    `create_kpi_card` method from the `comp_factory` component factory.

    Returns:
        html.Div: A division element containing the created KPI cards.
    """
    return html.Div(
        className="flex-wrapper",
        children=[
            comp_factory.create_kpi_card(
                title="Total Fraud Cases",
                icon_id=ID.FRAUD_KPI_TOTAL_FRAUD_ICON,
                div_id=ID.FRAUD_KPI_TOTAL_FRAUD_DIV_ID
            ),
            comp_factory.create_kpi_card(
                title="Fraud Ratio (%)",
                icon_id=ID.FRAUD_KPI_FRAUD_RATIO_ICON,
                div_id=ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID
            ),
        ]
    )



def _create_analysis_tabs() -> html.Div:
    """
    Creates an interactive dashboard component with multiple tabs for fraud analysis.

    This function generates a tabbed layout using Dash and Plotly components,
    organizing various types of fraud analyses into tabs such as "Overview",
    "Demographics", "Patterns", and "Cards & Merchants". Each tab contains multiple
    dashboard cards showcasing specific graphs and visualizations related to fraud
    data. The design integrates graphs for fraud trends, demographics, transaction
    patterns, and merchant/card details, styled for clear and organized
    presentation.

    Returns:
        html.Div: A Dash HTML division component containing the entire tabbed
        layout and its subcomponents.
    """
    return html.Div(
        className="fraud-analysis-tabs",
        children=[
            dcc.Tabs([
                dcc.Tab(label="Overview", children=[
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud Transactions per US State"),
                                dcc.Graph(id=ID.FRAUD_STATE_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Share of Online vs In-Store Transactions"),
                                dcc.Graph(id=ID.FRAUD_PIE_CHART, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Top Online Merchants by Fraud Count"),
                                dcc.Graph(id=ID.FRAUD_TOP_MERCHANTS, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                ]),
                dcc.Tab(label="Demographics", children=[
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Age Group"),
                                dcc.Graph(id=ID.FRAUD_DEMO_AGE_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Gender"),
                                dcc.Graph(id=ID.FRAUD_DEMO_GENDER_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Income"),
                                dcc.Graph(id=ID.FRAUD_DEMO_INCOME_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                ]),
                dcc.Tab(label="Patterns", children=[
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Hour of Day"),
                                dcc.Graph(id=ID.FRAUD_PATTERN_HOUR_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Weekday"),
                                dcc.Graph(id=ID.FRAUD_PATTERN_WEEKDAY_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Average Fraud Amount"),
                                dcc.Graph(id=ID.FRAUD_PATTERN_AMOUNT_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                ]),
                dcc.Tab(label="Cards & Merchants", children=[
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Card Type"),
                                dcc.Graph(id=ID.FRAUD_CARD_TYPE_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Fraud by Card Brand"),
                                dcc.Graph(id=ID.FRAUD_CARD_BRAND_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                    html.Div(className="tab-card-row", children=[
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Top Merchant Categories (MCC)"),
                                dcc.Graph(id=ID.FRAUD_MCC_GRAPH, style={"height": "340px", "width": "100%"}),
                            ]),
                            className="tab-card"
                        ),
                    ]),
                ]),
            ])
        ]
    )