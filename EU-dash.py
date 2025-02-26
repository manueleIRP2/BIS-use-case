from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd

# ---------------------------
# 1. Load dataset from BIS API
# ---------------------------
url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+BE+CZ+DE+DK+ES+FI+FR+GB+GR+HU+IE+IT+LU+NL+PL+PT+SE...C?format=csv"
df = pd.read_csv(url)

# Convert TIME_PERIOD to datetime
df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'], errors='coerce')
df = df.dropna(subset=['TIME_PERIOD'])

# Extract country list in alphabetical order
countries = sorted(df['BORROWERS_CTY'].unique())
dropdown_options = [{'label': 'All countries', 'value': 'all'}] + [{'label': c, 'value': c} for c in countries]

# ---------------------------
# 2. Create Dash app
# ---------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Credit-to-GDP Dashboard"

# Define a style for the navigation buttons
button_style = {
    'display': 'inline-block',
    'backgroundColor': '#4CAF50',
    'color': 'white',
    'padding': '10px 20px',
    'margin': '5px',
    'textDecoration': 'none',
    'borderRadius': '5px',
    'fontSize': '16px'
}

# Custom button styles for each link (feel free to adjust the colors)
nav_buttons = html.Div([
    dcc.Link('🏠 Home', href='/', style={**button_style, 'backgroundColor': '#4CAF50'}),
    dcc.Link('📈 Time Series', href='/time-series', style={**button_style, 'backgroundColor': '#2196F3'}),
    dcc.Link('📊 Statistics', href='/statistics', style={**button_style, 'backgroundColor': '#FF9800'}),
    dcc.Link('📉 Histogram', href='/histogram', style={**button_style, 'backgroundColor': '#F44336'}),
], style={'textAlign': 'center', 'padding': '10px'})

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav_buttons,
    html.Div(id='page-content')
])

# ---------------------------
# 3. Homepage - Dataset Preview
# ---------------------------
def homepage_layout():
    df_preview = df.head(10).copy()  # Copy to avoid modifying original dataframe

    # Drop columns that are completely empty
    df_preview = df_preview.dropna(axis=1, how='all')
    
    # Round only numeric columns
    numeric_cols = df_preview.select_dtypes(include=['float', 'int']).columns
    df_preview[numeric_cols] = df_preview[numeric_cols].round(2)
    
    # Replace remaining missing values with an empty string
    df_preview = df_preview.fillna('')

    return html.Div([
        html.H2("Dataset Preview"),
        dash_table.DataTable(
            data=df_preview.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df_preview.columns],
            style_table={'overflowX': 'auto', 'margin': 'auto', 'width': '90%'},
            page_size=10,  # Shows 10 rows per page (adjust if necessary)
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'minWidth': '100px', 'width': '150px', 'maxWidth': '200px'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ], style={'textAlign': 'center', 'padding': '20px'})

# ---------------------------
# 4. Time Series Page
# ---------------------------
def time_series_layout():
    return html.Div([
        html.H2("Credit-to-GDP Gap Time Series 📈"),
        dcc.Dropdown(
            id="country-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
        dcc.Graph(id="time-series-graph", style={'height': '700px', 'width': '80%', 'margin': 'auto'})
    ], style={'textAlign': 'center'})

@app.callback(
    Output("time-series-graph", "figure"),
    Input("country-dropdown", "value")
)
def update_time_series(selected_country):
    filtered_df = df if selected_country == 'all' else df[df['BORROWERS_CTY'] == selected_country]
    fig = px.line(
        filtered_df, x="TIME_PERIOD", y="OBS_VALUE", color="BORROWERS_CTY",
        title="Credit-to-GDP Gap Time Series",
        labels={"TIME_PERIOD": "Year", "OBS_VALUE": "Credit-to-GDP Gap", "BORROWERS_CTY": "Country"}
    )
    return fig

# ---------------------------
# 5. Statistics Page
# ---------------------------
def statistics_layout():
    return html.Div([
        html.H2("Descriptive Statistics 📊"),
        dcc.Dropdown(
            id="stats-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
        dash_table.DataTable(
            id='stats-table', 
            style_table={'overflowX': 'auto', 'width': '80%', 'margin': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    ], style={'textAlign': 'center'})

@app.callback(
    [Output('stats-table', 'data'), Output('stats-table', 'columns')],
    Input('stats-dropdown', 'value')
)
def update_statistics(selected_country):
    filtered_data = df if selected_country == 'all' else df[df['BORROWERS_CTY'] == selected_country]
    stats = filtered_data['OBS_VALUE'].describe().reset_index()
    stats.columns = ['Statistic', 'Value']
    return stats.to_dict('records'), [{"name": col, "id": col} for col in stats.columns]

# ---------------------------
# 6. Histogram Page
# ---------------------------
def histogram_layout():
    return html.Div([
        html.H2("Histogram of Quarterly Changes 📉"),
        dcc.Dropdown(
            id="histogram-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
        dcc.Graph(id="histogram-graph", style={'height': '700px', 'width': '80%', 'margin': 'auto'})
    ], style={'textAlign': 'center'})

@app.callback(
    Output("histogram-graph", "figure"),
    Input("histogram-dropdown", "value")
)
def update_histogram(selected_country):
    filtered_data = df if selected_country == 'all' else df[df['BORROWERS_CTY'] == selected_country]
    filtered_data = filtered_data.sort_values('TIME_PERIOD')
    filtered_data['QUARTERLY_CHANGE'] = filtered_data['OBS_VALUE'].diff()
    fig = px.histogram(
        filtered_data, x="QUARTERLY_CHANGE", nbins=120, title="Quarterly Changes Distribution",
        labels={"QUARTERLY_CHANGE": "Quarterly Change"}
    )
    return fig

# ---------------------------
# 7. URL Routing
# ---------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/time-series':
        return time_series_layout()
    elif pathname == '/statistics':
        return statistics_layout()
    elif pathname == '/histogram':
        return histogram_layout()
    else:
        return homepage_layout()

# ---------------------------
# 8. Run App
# ---------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
