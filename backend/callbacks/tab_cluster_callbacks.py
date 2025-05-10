from dash import Input, Output, callback, callback_context
from frontend.component_ids import IDs


@callback(
    Output(IDs.CLUSTER_DROPDOWN_OUTPUT, 'children'),
    Input(IDs.CLUSTER_DROPDOWN, 'value')
)
def update_cluster(value):
    ctx = callback_context
    print(ctx.triggered)
    return f'You have selected "{value}" '