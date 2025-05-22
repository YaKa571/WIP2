from frontend.component_ids import ID
from dash import html, Output, Input, callback
"""
callbacks of tab Merchant
"""
@callback(
    Output('radio-output', 'children'),
    Output(ID.MERCHANT_BTN_ALL_MERCHANTS, 'className'),
    Output(ID.MERCHANT_BTN_MERCHANT_GROUP, 'className'),
    Output(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'className'),
    Input(ID.MERCHANT_BTN_ALL_MERCHANTS, 'n_clicks'),
    Input(ID.MERCHANT_BTN_MERCHANT_GROUP, 'n_clicks'),
    Input(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'n_clicks'),
)
def update_merchant(n1, n2, n3):
    buttons = {'opt1': n1, 'opt2': n2, 'opt3': n3}
    selected = max(buttons, key=buttons.get)

    def cls(opt): return 'option-btn selected' if selected == opt else 'option-btn'

    return f' {selected}', cls('opt1'), cls('opt2'), cls('opt3')