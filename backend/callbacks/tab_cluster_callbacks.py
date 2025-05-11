from dash import Input, Output, callback, callback_context
from frontend.component_ids import ID


@callback(
    Output(ID.CLUSTER_DROPDOWN_OUTPUT, 'children'),
    Input(ID.CLUSTER_DROPDOWN, 'value')
)
def update_cluster(value):
#    ctx = callback_context
#    print(ctx.triggered)

    if value=="Default":
        print("Cluster: Default")
    elif value=="Age Group":
        print("Cluster: Age Group")
    elif value=="Income vs Expenditures":
        print("Cluster: Income vs Expenditures")
    else:
        print("Error")
    return f'Cluster: "{value}" '