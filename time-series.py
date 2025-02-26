from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# ---------------------------
# 1. Load dataset from BIS API
# ---------------------------
url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+BE+CZ+DE+DK+ES+FI+FR+GB+GR+HU+IE+IT+LU+NL+PL+PT+SE...C?format=csv"
df = pd.read_csv(url)
df_subset = df[['BORROWERS_CTY', 'TIME_PERIOD', 'OBS_VALUE']].copy()

# Convert TIME_PERIOD in datetime 
df_subset['TIME_PERIOD'] = pd.to_datetime(df_subset['TIME_PERIOD'], errors='coerce')
df_subset = df_subset.dropna(subset=['TIME_PERIOD'])

# Extract country list in alphabetical order
countries = sorted(df_subset['BORROWERS_CTY'].unique())

# ---------------------------
# 2. Create dash app
# ---------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H4(''),
    dcc.Dropdown(
        id="country-dropdown",
        options=[{'label': country, 'value': country} for country in countries],
        value=countries,  # show all time series by default
        multi=True
    ),
        dcc.Graph(id="time-series-graph", style={'height': '600px'})
    ],
    style={'width': '70%', 'margin': '0 auto'}  # 80% width and centered
)

@app.callback(
    Output("time-series-graph", "figure"), 
    Input("country-dropdown", "value"))
def update_line_chart(selected_countries):
    # if you don't select anything specific it displays all countries
    if not selected_countries:
        filtered_df = df_subset
    else:
        filtered_df = df_subset[df_subset['BORROWERS_CTY'].isin(selected_countries)]
    
    fig = px.line(
        filtered_df, 
        x="TIME_PERIOD", 
        y="OBS_VALUE", 
        color="BORROWERS_CTY",
        title="Credit-to-GDP Gap time series for European Union countries",
        labels={"TIME_PERIOD": "Year", "OBS_VALUE": "Credit-to-GDP Gap", "BORROWERS_CTY": "Country"}
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
