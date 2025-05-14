from dash import callback, Output, Input

from backend.data_manager import DataManager
from components.rightcolumn.tabs.tab_home import create_pie_graph
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()


@callback(
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_GENDER, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_AGE, "figure"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks")
)
def update_pie_graphs(n_clicks):
    dark_mode = n_clicks % 2 == 1

    gender_data = dm.calc_expenditures_by_gender()
    channel_data = dm.calc_expenditures_by_channel()
    age_data = dm.calc_expenditures_by_age()
    return (
        create_pie_graph(data=gender_data, showlegend=False),
        create_pie_graph(data=channel_data, showlegend=False, colors=["#FFCD00", "#81C784"]),
        create_pie_graph(age_data, dark_mode=dark_mode, showlegend=False, textinfo="label")
    )
