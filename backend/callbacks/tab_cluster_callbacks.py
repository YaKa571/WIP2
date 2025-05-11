from dash import Input, Output, callback, callback_context
from frontend.component_ids import ID


@callback(
    Output(ID.CLUSTER_DROPDOWN_OUTPUT, 'children'),
    Input(ID.CLUSTER_DROPDOWN, 'value')
)
def update_cluster(value):
#    ctx = callback_context
#    print(ctx.triggered)
    return f'Cluster: "{value}" '