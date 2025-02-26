import dash
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas as pd

# ---------------------------
# 1. load dataset
# ---------------------------
url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+BE+CZ+DE+DK+ES+FI+FR+GB+GR+HU+IE+IT+LU+NL+PL+PT+SE...C?format=csv"
df = pd.read_csv(url)
df_subset = df[['BORROWERS_CTY', 'TIME_PERIOD', 'OBS_VALUE']].copy()

# Convert TIME_PERIOD in datetime
df_subset['TIME_PERIOD'] = pd.to_datetime(df_subset['TIME_PERIOD'], errors='coerce')
df_subset = df_subset.dropna(subset=['TIME_PERIOD'])

# Lista degli stati in ordine alfabetico
states = sorted(df_subset['BORROWERS_CTY'].unique())

# Opzioni per il dropdown: includiamo "Tutti gli Stati" con valore 'all'
dropdown_options = [{'label': 'All countries', 'value': 'all'}] + [{'label': s, 'value': s} for s in states]

# ---------------------------
# 2. Dash app
# ---------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H4("Dashboard: Descriptive statistics of Credit-to-GDP ratio for European Union countries"),
    dcc.Dropdown(
        id="state-dropdown",
        options=dropdown_options,
        value='all',  # show average of all countries by default
        clearable=False
    ),
    dash_table.DataTable(
        id='desc-table',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    )
], style={'width': '90%', 'margin': '0 auto'})

@app.callback(
    Output('desc-table', 'data'),
    Output('desc-table', 'columns'),
    Input('state-dropdown', 'value')
)
def update_table(selected_state):
    if selected_state == 'all':
        # compute statistics
        desc_stats = df_subset['OBS_VALUE'].describe().reset_index()
    else:
        # Filter for selected country
        desc_stats = df_subset[df_subset['BORROWERS_CTY'] == selected_state]['OBS_VALUE'].describe().reset_index()
    
    desc_stats.columns = ['Statistic', 'Value']
    data = desc_stats.to_dict('records')
    columns = [{"name": col, "id": col} for col in desc_stats.columns]
    return data, columns

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
