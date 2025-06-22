import dash_bootstrap_components as dbc
from dash import dcc, html

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

def create_fraud_content():
    return html.Div(
        children=[
            _create_heading(),
            _create_kpi_cards(),
            _create_analysis_tabs().children,
            
        ],
        className="tab-content-inner fraud-tab"
    )

def _create_heading() -> html.Div:
    """
    Generates the heading for the Fraud tab including the info icon and tooltip.
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
    Displays fraud-related KPIs such as total fraud cases and fraud ratio.
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
            ),
        ]
    )

def _create_analysis_tabs() -> html.Div:
    """
    Creates all tab panels for fraud analysis using manually styled tab structure.
    """
    return html.Div(
        className="fraud-analysis-tabs",
        children=[
            html.Div(
                className="custom-tab-bar",
                children=[
                    html.Button("Overview", id=ID.FRAUD_ANALYSIS_TAB_OVERVIEW, className="custom-tab-button"),
                    html.Button("Demographics", id=ID.FRAUD_ANALYSIS_TAB_DEMOGRAPHICS, className="custom-tab-button"),
                    html.Button("Patterns", id=ID.FRAUD_ANALYSIS_TAB_PATTERNS, className="custom-tab-button"),
                    html.Button("Cards & Merchants", id=ID.FRAUD_ANALYSIS_TAB_CARDS, className="custom-tab-button")
                ]
            ),
            _create_tab_item(ID.FRAUD_ANALYSIS_TAB_OVERVIEW_CONTENT, [
                _create_fraud_graph_row([
                    ("Fraud Transactions per US State", ID.FRAUD_STATE_GRAPH),
                    ("Share of Online vs In-Store Transactions", ID.FRAUD_PIE_CHART),
                ]),
                _create_fraud_graph_row([
                    ("Top Online Merchants by Fraud Count", ID.FRAUD_TOP_MERCHANTS),
                ])
            ]),
            _create_tab_item(ID.FRAUD_ANALYSIS_TAB_DEMOGRAPHICS_CONTENT, [
                _create_fraud_graph_row([
                    ("Fraud by Age Group", ID.FRAUD_DEMO_AGE_GRAPH),
                    ("Fraud by Gender", ID.FRAUD_DEMO_GENDER_GRAPH),
                ]),
                _create_fraud_graph_row([
                    ("Fraud by Income", ID.FRAUD_DEMO_INCOME_GRAPH),
                ])
            ]),
            _create_tab_item(ID.FRAUD_ANALYSIS_TAB_PATTERNS_CONTENT, [
                _create_fraud_graph_row([
                    ("Fraud by Hour of Day", ID.FRAUD_PATTERN_HOUR_GRAPH),
                    ("Fraud by Weekday", ID.FRAUD_PATTERN_WEEKDAY_GRAPH),
                ]),
                _create_fraud_graph_row([
                    ("Average Fraud Amount", ID.FRAUD_PATTERN_AMOUNT_GRAPH),
                ])
            ]),
            _create_tab_item(ID.FRAUD_ANALYSIS_TAB_CARDS_CONTENT, [
                _create_fraud_graph_row([
                    ("Fraud by Card Type", ID.FRAUD_CARD_TYPE_GRAPH),
                    ("Fraud by Card Brand", ID.FRAUD_CARD_BRAND_GRAPH),
                ]),
                _create_fraud_graph_row([
                    ("Top Merchant Categories (MCC)", ID.FRAUD_MCC_GRAPH),
                ])
            ])
        ]
    )

def _create_tab_item(tab_content_id: str, children: list) -> html.Div:
    return html.Div(id=tab_content_id, className="tab-item hidden", children=children)

def _create_fraud_graph_row(cards: list[tuple[str, str]]) -> html.Div:
    return html.Div(
        className="flex-wrapper",
        children=[
            _create_fraud_graph_card(title, graph_id) for title, graph_id in cards
        ]
    )

def _create_fraud_graph_card(title: str, graph_id: str) -> dbc.Card:
    return dbc.Card(
        className="graph-card",
        children=[
            dbc.CardHeader(html.P(title, className="graph-card-title")),
            dbc.CardBody(
                dcc.Graph(id=graph_id, config={"displayModeBar": False}, className="bar-chart")
            )
        ]
    )
