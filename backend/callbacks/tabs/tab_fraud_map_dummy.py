from dash import Output, Input, callback
import plotly.express as px
import pandas as pd

# Dummy-Daten: Fraud-Summen pro Bundesstaat
dummy_data = {
    "CA": 72000,
    "TX": 61000,
    "NY": 54000,
    "FL": 43000,
    "IL": 39000,
    "PA": 35000,
    "OH": 32000,
    "GA": 30000,
    "NC": 28000,
    "MI": 26000,
}

@callback(
    Output("fraud-map", "figure"),
    Input("app-init-trigger", "children")  # beim App-Start
)
def update_fraud_map(_):
    df = pd.DataFrame({
        "state": list(dummy_data.keys()),
        "value": list(dummy_data.values())
    })

    fig = px.choropleth(
        df,
        locations="state",
        locationmode="USA-states",
        color="value",
        scope="usa",
        color_continuous_scale="Reds",
        title="Fraud Volume by State (Dummy)"
    )

    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    return fig
