import time

start_time = time.perf_counter()

import dash_bootstrap_components as dbc
from dash import Dash, html

import components.component_factory as comp_factory
from backend.callbacks.data_table_callbacks import DataTableCallbacks  # noqa: F401 (don't remove this comment!)
from backend.data_manager import data_frame_users, data_frame_transactions, data_frame_cards
from components.left_column import create_left_column
from components.right_column import create_right_column
from frontend.component_ids import IDs
from frontend.styles import STYLES, Style


# JSON files, normalized to fit format
# with open(r'assets\data\mcc_codes.json', 'r', encoding='utf-8') as f:
#    data_mcc = json.load(f)
#    data_frame_mcc = pd.json_normalize(data_mcc)


# TODO: Too much loading time
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
                        comp_factory.create_data_table(IDs.TABLE_USERS, data_frame_users, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_TRANSACTIONS, data_frame_transactions, visible=False),
                        comp_factory.create_data_table(IDs.TABLE_CARDS, data_frame_cards, visible=False),
                        # comp_factory.create_data_table("table3", data_frame_mcc, visible=False),

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
    startup_time = time.perf_counter() - start_time
    print(f"🚀 Dash App ready in {startup_time:.2f} seconds.")
    app.run(debug=True)
