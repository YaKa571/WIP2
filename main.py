import dash_bootstrap_components as dbc
from dash import Dash, html, dash_table

import backend.data_manager as data_manager
import components.component_factory as comp_factory
from components.left_column import create_left_column
from components.right_column import create_right_column
from frontend.styles import STYLES, Style
import pandas as pd
import json

data_frame_users = data_manager.read_csv_data("users_data.csv", sort_alphabetically=True)
data_frame_transactions = data_manager.read_csv_data("transactions_data.csv", sort_alphabetically=True)
data_frame_cards = data_manager.read_csv_data("cards_data.csv", sort_alphabetically=True)

#json files, normalized to fit format
with open(r'assets\data\mcc_codes.json', 'r', encoding='utf-8') as f:
    data_mcc = json.load(f)
    data_frame_mcc = pd.json_normalize(data_mcc)
# TODO: to much loading time
# with open(r'assets\data\train_fraud_labels.json', 'r', encoding='utf-8') as f:
#     data_train_fraud = json.load(f)
#     data_frame_train_fraud = pd.json_normalize(data_train_fraud)

def create_app():
    external_style = [dbc.themes.BOOTSTRAP]
    app = Dash(__name__, external_stylesheets=external_style)

    app.layout = dbc.Container(
        [
            # Row with Title
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(
                            "Financial Transactions Dashboard",
                            className="text-center m-0 pb-3",
                            style=STYLES[Style.APP_TITLE]
                        ),

                        # To have a look at a certain data table, add it here and set visible=True
                        comp_factory.create_data_table("table1",data_frame_users , visible=False),
                        comp_factory.create_data_table("table2", data_frame_cards, visible=False),
                        comp_factory.create_data_table("table3", data_frame_mcc, visible=False),

                        # first 1000 rows of transactions_data as table, uncomment to display
                        # dash_table.DataTable(
                        #     id='table',
                        #     columns=[{"name": i, "id": i} for i in data_frame_transactions.columns],
                        #     data=data_frame_transactions.head(1000).to_dict('records'),
                        #     page_size=20
                        # )
                    ]
                )
            ),

            # Row with Left and Right Column
            dbc.Row(
                [
                    create_left_column(),
                    create_right_column()
                ],
                className="gx-3",
                style={"height": "calc(100vh - 6rem)"}
            )
        ],
        fluid=True,
        className="p-3 m-0",
        style=STYLES[Style.BODY]
    )

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
