from dash import Input, Output, callback



@callback(
    Output('cluster-dropdown-output', 'children'),
    Input('cluster-dropdown', 'value')
)
def update_cluster(value):
    print(value)
    return f'You have selected "{value}" '