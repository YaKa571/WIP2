from backend.data_setup.tabs import tab_cluster_data_setup
from dash import dcc, html, callback, Input, Output

from backend.data_setup.tabs.tab_cluster_data_setup import prepare_cluster_data, make_cluster_plot, my_data_file, \
    create_cluster_legend, prepare_inc_vs_exp_cluster_data, make_inc_vs_exp_plot
from frontend.component_ids import ID
import plotly.express as px

def cls(opt, selected):
    """
        Returns the CSS class string for cluster mode buttons (Total Value, Average Value, Inc vs Exp).
        Marks the button as 'selected' if the option matches the selected state.

        Args:
            opt (str): The option identifier.
            selected (str): The currently selected option identifier.

        Returns:
            str: The CSS class string for the button.
        """
    return 'option-btn selected' if selected == opt else 'option-btn'


@callback(
    Output(ID.CLUSTER_BTN_TOTAL_VALUE, 'className'),
    Output(ID.CLUSTER_BTN_AVERAGE_VALUE, 'className'),
    Output(ID.CLUSTER_BTN_INC_VS_EXP, 'className'),
    Output(ID.CLUSTER_BTN_ALL_AGES, 'className'),
    Output(ID.CLUSTER_BTN_AGE_GROUP, 'className'),
    Output(ID.CLUSTER_GRAPH, 'figure'),
    Output(ID.CLUSTER_LEGEND, 'children'),
    Input(ID.CLUSTER_BTN_TOTAL_VALUE,'n_clicks'),
    Input(ID.CLUSTER_BTN_AVERAGE_VALUE,'n_clicks'),
    Input(ID.CLUSTER_BTN_INC_VS_EXP,'n_clicks'),
    Input(ID.CLUSTER_BTN_ALL_AGES,'n_clicks'),
    Input(ID.CLUSTER_BTN_AGE_GROUP,'n_clicks'),
    Input(ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN,'value'),
)
def update_cluster(n_total_value, n_average_value, n_inc_vs_exp,n_all_ages,n_age_groups, selected_merchant_group):
    """
        Callback function to update the cluster tab UI state based on user interaction.
        It manages selection states for cluster display modes (Total Value, Average Value, Income vs Expenses),
        age grouping (all ages or grouped by age), and merchant group filter.
        Returns updated button classes, cluster plot figure, and cluster legend.

        Args:
            n_total_value (int): Number of clicks on "Total Value" button.
            n_average_value (int): Number of clicks on "Average Value" button.
            n_inc_vs_exp (int): Number of clicks on "Inc vs Exp" button.
            n_all_ages (int): Number of clicks on "All Ages" button.
            n_age_groups (int): Number of clicks on "Age Groups" button.
            selected_merchant_group (str): Selected merchant group from dropdown.

        Returns:
            tuple:
                - className for Total Value button (str)
                - className for Average Value button (str)
                - className for Income vs Expenses button (str)
                - className for All Ages button (str)
                - className for Age Groups button (str)
                - figure for cluster graph (plotly.graph_objs._figure.Figure)
                - children for cluster legend (list or html.Div)
        """
    clicks_1 = {'opt1': n_total_value or 0, 'opt2': n_average_value or 0, 'opt3': n_inc_vs_exp or 0}
    selected_1 = max(clicks_1, key=clicks_1.get) if any(clicks_1.values()) else 'opt1'

    clicks_2 = {'opt4': n_all_ages or 0, 'opt5': n_age_groups or 0}
    selected_2 = max(clicks_2, key=clicks_2.get) if any(clicks_2.values()) else 'opt4'

    if selected_1 == 'opt1' and selected_2 == 'opt4':
        #print('1 4')
        df_clustered = prepare_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_cluster_plot(df_clustered, mode='total_value', age_group_mode='not grouped')
        legend = create_cluster_legend(mode='total_value', df=df_clustered)
    elif selected_1 == 'opt1' and selected_2 == 'opt5':
        #print('1 5')
        df_clustered = prepare_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_cluster_plot(df_clustered, mode='total_value', age_group_mode='grouped')
        legend = create_cluster_legend(mode='total_value', df=df_clustered)
    elif selected_1 == 'opt2' and selected_2 == 'opt4':
        #print('2 4')
        df_clustered = prepare_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_cluster_plot(df_clustered, mode='average_value', age_group_mode='not grouped')
        legend = create_cluster_legend(mode='average_value', df=df_clustered)
    elif selected_1 == 'opt2' and selected_2 == 'opt5':
        #print('2 5')
        df_clustered = prepare_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_cluster_plot(df_clustered, mode='average_value', age_group_mode='grouped')
        legend = create_cluster_legend(mode='average_value', df=df_clustered)
    elif selected_1 == 'opt3' and selected_2 == 'opt4':
        #print('3 4')
        df_clustered = prepare_inc_vs_exp_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_inc_vs_exp_plot(df_clustered, age_group_mode='not grouped')
        legend = create_cluster_legend(mode='inc_vs_exp', df=df_clustered)
    elif selected_1 == 'opt3' and selected_2 == 'opt5':
        #print('3 5')
        df_clustered = prepare_inc_vs_exp_cluster_data(my_data_file, merchant_group=selected_merchant_group)
        fig = make_inc_vs_exp_plot(df_clustered, age_group_mode='grouped')
        legend = create_cluster_legend(mode='inc_vs_exp', df=df_clustered)
    else:
        #print('else')
        fig = px.scatter()
        legend = html.Div([html.P('No Legend')])
    return (
        cls('opt1', selected_1),
        cls('opt2', selected_1),
        cls('opt3', selected_1),
        cls('opt4', selected_2),
        cls('opt5', selected_2),
        fig,
        legend
    )

def get_cluster_merchant_group_input_container():
    """
        Creates the dropdown input container for selecting a merchant group in the cluster tab.
        The dropdown options are populated dynamically from available merchant groups.
        Sets the first merchant group as the default selection if available.

        Returns:
            html.Div: A Div containing the labeled dropdown input for merchant group selection.
        """
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