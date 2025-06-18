import dash_bootstrap_components as dbc
from dash import dcc, html

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID


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
        className="tab-content-inner fraud-tab",
        children=[

            _create_heading(),
            _create_kpi_cards(),
            _create_overview_section(),
            _create_detailed_analysis_section(),

        ],
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
            html.H4("Fraud Overview", id=ID.FRAUD_TAB_HEADING, className="green-text"),
            comp_factory.create_info_icon(ID.FRAUD_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.FRAUD_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[

                    "This tab shows potentially fraudulent activity, trends,",
                    html.Br(),
                    "and visualizations based on transaction and card data.",

                ]
            )
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
                icon_id=IconID.FRAUD,
                div_id=ID.FRAUD_KPI_TOTAL_FRAUD_DIV_ID
            ),
            comp_factory.create_kpi_card(
                title="Fraud Ratio (%)",
                icon_id=IconID.FUEL,
                div_id=ID.FRAUD_KPI_FRAUD_RATIO_DIV_ID
            )

        ]
    )


def _create_overview_section() -> html.Div:
    """
    Creates the overview section for the fraud tab.

    This section contains key visualizations for fraud analysis including
    a map of fraud transactions by state and a pie chart showing online vs in-store
    transactions. The layout uses flex-wrapper for responsive design.

    Returns:
        html.Div: A Div component containing the overview visualizations.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            comp_factory.create_circle_diagram_card(
                icon_id=IconID.BAR_CHART_LINE_FILL,
                title=["Fraud Transactions", "per US State"],
                graph_id=ID.FRAUD_STATE_GRAPH,
            ),
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.CART,
                title=["Online vs In-Store", "Transactions"],
                graph_id=ID.FRAUD_PIE_CHART,
            )

        ]
    )


def _create_detailed_analysis_section() -> html.Div:
    """
    Creates an interactive dashboard component with multiple tabs for detailed fraud analysis.

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
        className="flex-wrapper flex-fill",
        children=[

            dbc.Card(
                className="graph-card with-bar-chart",
                children=[

                    dbc.CardHeader(
                        children=[

                            # Custom Tab Bar
                            html.Div(
                                className="d-flex custom-tab-bar",
                                children=[
                                    dbc.Button(
                                        "Overview",
                                        id=ID.FRAUD_ANALYSIS_TAB_OVERVIEW,
                                        n_clicks=0,
                                        className="custom-tab-button active"
                                    ),
                                    dbc.Button(
                                        "Demographics",
                                        id=ID.FRAUD_ANALYSIS_TAB_DEMOGRAPHICS,
                                        n_clicks=0,
                                        className="custom-tab-button"
                                    ),
                                    dbc.Button(
                                        "Patterns",
                                        id=ID.FRAUD_ANALYSIS_TAB_PATTERNS,
                                        n_clicks=0,
                                        className="custom-tab-button"
                                    ),
                                    dbc.Button(
                                        "Cards",
                                        id=ID.FRAUD_ANALYSIS_TAB_CARDS,
                                        n_clicks=0,
                                        className="custom-tab-button"
                                    ),
                                    dbc.Button(
                                        "Merchants",
                                        id=ID.FRAUD_ANALYSIS_TAB_MERCHANTS,
                                        n_clicks=0,
                                        className="custom-tab-button"
                                    )
                                ]
                            )

                        ]
                    ),
                    dbc.CardBody(
                        className="d-flex flex-column p-0",
                        children=[

                            # Tab Content Wrapper
                            html.Div(
                                id="fraud-analysis-tab-content",
                                className="tab-content-wrapper flex-fill",
                                children=[

                                    # Overview Tab Content
                                    html.Div(
                                        id=ID.FRAUD_ANALYSIS_CONTENT_OVERVIEW,
                                        className="tab-item active",
                                        children=[
                                            html.Div(
                                                className="flex-wrapper",
                                                children=[

                                                    dcc.Graph(
                                                        id=ID.FRAUD_TOP_MERCHANTS,
                                                        responsive=True,
                                                        style={"height": "100%", "width": "100%"}
                                                    )

                                                ]
                                            )
                                        ]
                                    ),

                                    # Demographics Tab Content
                                    html.Div(
                                        id=ID.FRAUD_ANALYSIS_CONTENT_DEMOGRAPHICS,
                                        className="tab-item hidden",
                                        children=[
                                            html.Div(
                                                className="flex-wrapper",
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_DEMO_AGE_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_DEMO_GENDER_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                className="flex-wrapper",
                                                style={"marginTop": "var(--gutter)"},
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_DEMO_INCOME_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    ),

                                    # Patterns Tab Content
                                    html.Div(
                                        id=ID.FRAUD_ANALYSIS_CONTENT_PATTERNS,
                                        className="tab-item hidden",
                                        children=[
                                            html.Div(
                                                className="flex-wrapper",
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_PATTERN_HOUR_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_PATTERN_WEEKDAY_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                className="flex-wrapper",
                                                style={"marginTop": "var(--gutter)"},
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_PATTERN_AMOUNT_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    ),

                                    # Cards & Merchants Tab Content
                                    html.Div(
                                        id=ID.FRAUD_ANALYSIS_CONTENT_CARDS,
                                        className="tab-item hidden",
                                        children=[
                                            html.Div(
                                                className="flex-wrapper",
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_CARD_TYPE_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_CARD_BRAND_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    ),

                                    # Merchants Tab Content
                                    html.Div(
                                        id=ID.FRAUD_ANALYSIS_CONTENT_MERCHANTS,
                                        className="tab-item hidden",
                                        children=[
                                            html.Div(
                                                className="flex-wrapper",
                                                children=[
                                                    dbc.Card(
                                                        className="graph-card",
                                                        children=[
                                                            dbc.CardBody(
                                                                children=[
                                                                    dcc.Graph(
                                                                        id=ID.FRAUD_MCC_GRAPH,
                                                                        responsive=True,
                                                                        style={"height": "100%", "width": "100%"}
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )