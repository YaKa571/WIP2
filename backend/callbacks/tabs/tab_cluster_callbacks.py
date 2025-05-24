from backend.data_setup.tabs import tab_cluster_data_setup
from dash import dcc, html, callback, Input, Output
from frontend.component_ids import ID
import plotly.express as px

def cls_1(opt, selected):
    return 'option-btn selected' if selected == opt else 'option-btn'
def cls_2(opt, selected):
    return 'option-btn selected' if selected == opt else 'option-btn'

# @callback(
#     Output(ID.CLUSTER_BTN_TRANSACTIONS, 'className'),
#     Output(ID.CLUSTER_BTN_VALUE, 'className'),
#     Output(ID.CLUSTER_BTN_INC_VS_EXP, 'className'),
#     Output(ID.CLUSTER_BTN_ALL_AGES, 'className'),
#     Output(ID.CLUSTER_BTN_AGE_GROUP, 'className'),
#     Output(ID.CLUSTER_GRAPH, 'figure'),
#     Output(ID.CLUSTER_LEGEND, 'children'),
#     Input(ID.CLUSTER_BTN_TRANSACTIONS,'n_clicks'),
#     Input(ID.CLUSTER_BTN_VALUE,'n_clicks'),
#     Input(ID.CLUSTER_BTN_INC_VS_EXP,'n_clicks'),
#     Input(ID.CLUSTER_BTN_ALL_AGES,'n_clicks'),
#     Input(ID.CLUSTER_BTN_AGE_GROUP,'n_clicks'),
#     Input(ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN,'value'),
# )
# def update_cluster(n_transactions, n_value, n_inc_vs_exp,n_all_ages,n_age_groups, selected_merchant_group):
#     clicks_1 = {'opt1': n_transactions or 0, 'opt2': n_value or 0, 'opt3': n_inc_vs_exp or 0}
#     selected_1 = max(clicks_1, key=clicks_1.get) if any(clicks_1.values()) else 'opt1'
#
#     clicks_2 = {'opt4': n_all_ages or 0, 'opt5': n_age_groups or 0}
#     selected_2 = max(clicks_2, key=clicks_2.get) if any(clicks_2.values()) else 'opt4'
#
#     if selected_1 == 'opt1' and selected_2 == 'opt4':
#         print('1 4')
#     elif selected_1 == 'opt1' and selected_2 == 'opt5':
#         print('1 5')
#     elif selected_1 == 'opt2' and selected_2 == 'opt4':
#         print('2 4')
#     elif selected_1 == 'opt2' and selected_2 == 'opt5':
#         print('2 5')
#     elif selected_1 == 'opt3' and selected_2 == 'opt4':
#         print('3 4')
#     elif selected_1 == 'opt3' and selected_2 == 'opt5':
#         print('3 5')
#     else:
#         print('else')
#     fig = px.scatter()
#     legend = html.Div([html.P('Legende')])
#     return (
#         cls_1('opt1', selected_1),
#         cls_1('opt2', selected_1),
#         cls_1('opt3', selected_1),
#         cls_2('opt4', selected_2),
#         cls_2('opt5', selected_2),
#         fig,
#         legend
#     )





def get_cluster_merchant_group_input_container():
    my_merchant_groups = tab_cluster_data_setup.get_cluster_merchant_group_dropdown()
    options = [{'label': group, 'value': group} for group in my_merchant_groups]

    default_value = my_merchant_groups[0] if my_merchant_groups else None

    return html.Div([
        html.Label("Select Merchant Group:", className="dropdown-label"),
        dcc.Dropdown(
            id=ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN,
            options=options,
            value=default_value,
            placeholder="Choose a merchant group...",
            searchable=True,
            multi=False,
            style={"width": "100%"}
        )
    ],
        className="dropdown-container"
    )