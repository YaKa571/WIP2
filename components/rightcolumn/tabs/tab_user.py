from dash import html, dcc

# TODO: @Son
def create_user_content():
    return html.Div(
        [
            # Drei Suchleisten nebeneinander mit Lupe
            html.Div(
                [
                    # Linke Suchleiste – Name
                    html.Div(
                        [
                            html.Img(src="/assets/icons/lens-search.svg", className="search-icon"),
                            dcc.Input(
                                id='name-search-input',
                                type='text',
                                placeholder='Search by Name',
                                className='search-input',
                            )
                        ],
                        className="search-wrapper p-2 flex-grow-1 me-2"
                    ),

                    # Mittlere Suchleiste – User-ID
                    html.Div(
                        [
                            html.Img(src="/assets/icons/lens-search.svg", className="search-icon"),
                            dcc.Input(
                                id='user-id-search-input',
                                type='text',
                                placeholder='Search by User ID',
                                className='search-input',
                            )
                        ],
                        className="search-wrapper p-2 flex-grow-1 me-2"
                    ),

                    # Rechte Suchleiste – Card-ID
                    html.Div(
                        [
                            html.Img(src="/assets/icons/lens-search.svg", className="search-icon"),
                            dcc.Input(
                                id='card-id-search-input',
                                type='text',
                                placeholder='Search by Card ID',
                                className='search-input',
                            )
                        ],
                        className="search-wrapper p-2 flex-grow-1"
                    ),
                ],
                className="d-flex mb-4"
            ),

            # KPI-Boxen (Platzhalter)
            # Vier obere KPI-Boxen
            html.Div(
                [
                    html.Div("Amount of Transactions", className="user-kpi-box"),
                    html.Div("Total Sum", className="user-kpi-box"),
                    html.Div("Average Amount", className="user-kpi-box"),
                    html.Div("Amount of Cards", className="user-kpi-box"),
                ],
                className="d-flex justify-content-between mb-4"
            ),

            # Neue mittige Box für Credit Limit
            html.Div(
                "Credit Limit",
                className="user-credit-limit-box my-2 mx-auto"
            ),

            # Ergebnisbereich (z. B. Tabelle später)
            html.Div(id='search-results', className="mt-4"),
        ],
        className="tab-content-wrapper flex-fill"
    )
