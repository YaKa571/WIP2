from dash import Input, Output, callback, callback_context



@callback(
    Output('cluster-dropdown-output', 'children'),
    Input('cluster-dropdown', 'value')
)
def update_cluster(value):
    ctx = callback_context
    print(ctx.triggered)
    return f'You have selected "{value}" '