import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# ---------------------------
# 1. Define Data Sources
# ---------------------------
DATA_GROUPS = {
    "EU": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+BE+CZ+DE+DK+ES+FI+FR+GB+GR+HU+IE+IT+LU+NL+PL+PT+SE...C?format=csv",
    "G20": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AR+AU+BR+CA+CN+DE+FR+GB+ID+IN+IT+JP+KR+MX+RU+SA+TR+US+ZA?format=csv",
    "Euro-area": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+BE+DE+ES+FI+FR+GR+IE+IT+LU+NL+PT+XM?format=csv",
    "G8": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.CA+DE+FR+GB+IT+JP+RU+US?format=csv",
    "OECD": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/.AT+AU+BE+CA+CH+CL+CO+CZ+DE+DK+ES+FI+FR+GB+GR+HU+IE+IL+IT+JP+KR+LU+MX+NL+NO+NZ+PL+PT+SE+TR+US?format=csv"
}
DEFAULT_DATASET = "EU"

def load_data(url):
    df = pd.read_csv(url)
    df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'], errors='coerce')
    df = df.dropna(subset=['TIME_PERIOD'])
    df['DAILY_CHANGE'] = df.groupby('BORROWERS_CTY')['OBS_VALUE'].diff()
    return df

# Initially load default dataset (will be updated later based on selection)
df = load_data(DATA_GROUPS[DEFAULT_DATASET])
df_preview = df.head(10).copy().round(2)  # Change number here to display more rows
countries = sorted(df['BORROWERS_CTY'].unique())
dropdown_options = [{'label': 'All countries', 'value': 'all'}] + [{'label': c, 'value': c} for c in countries]

# ---------------------------
# 2. Initialize Dash App with Bootstrap
# ---------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Credit-to-GDP Dashboard"

# The main layout includes a dcc.Store to hold the selected dataset group
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-dataset', data=DEFAULT_DATASET),
    html.Div(id='page-content')
])

# ---------------------------
# 3. Page Layouts
# ---------------------------

# 3a. Selection Page – Choose a Data Group
selection_layout = html.Div([
    dbc.NavbarSimple(
        children=[],
        brand="Credit-to-GDP Analysis",
        color="dark",
        dark=True,
        className="mb-4"
    ),
    dbc.Container([
        html.H2("Select Data Group", className="text-center mt-4"),
        dcc.Dropdown(
            id="group-dropdown",
            options=[{'label': key, 'value': key} for key in DATA_GROUPS.keys()],
            value=DEFAULT_DATASET,
            clearable=False
        ),
        html.Br(),
        dbc.Button("Proceed to Dashboard", id="proceed-button", color="primary")
    ], fluid=True)
])

# 3b. Preview (Homepage) – Dataset Preview (all columns)
home_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("🏠 Home", href="/preview", className="nav-link")),
            dbc.NavItem(dcc.Link("📈 Time Series", href="/time-series", className="nav-link")),
            dbc.NavItem(dcc.Link("📊 Statistics", href="/statistics", className="nav-link")),
            dbc.NavItem(dcc.Link("📉 Histogram", href="/histogram", className="nav-link")),
            dbc.NavItem(dcc.Link("🔄 Change Dataset", href="/", className="nav-link"))
        ],
        brand="Credit-to-GDP Analysis",
        color="dark",
        dark=True,
        className="mb-4"
    ),
    dbc.Container([
        html.H2("🏠 Dataset Preview", className="text-center mt-4"),
        html.P("This dashboard provides an analysis of the Credit-to-GDP gap. Below is a sample of the dataset.", className="text-center"),
        dash_table.DataTable(
            id='preview-table',
            columns=[{"name": col, "id": col} for col in df_preview.columns],
            data=df_preview.to_dict('records'),
            style_table={'overflowX': 'auto', 'width': '100%'},
            style_cell={'textAlign': 'left'}
        )
    ], fluid=True, className="my-4")
])

# 3c. Time Series Page
time_series_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("🏠 Home", href="/preview", className="nav-link")),
            dbc.NavItem(dcc.Link("📈 Time Series", href="/time-series", className="nav-link")),
            dbc.NavItem(dcc.Link("📊 Statistics", href="/statistics", className="nav-link")),
            dbc.NavItem(dcc.Link("📉 Histogram", href="/histogram", className="nav-link")),
            dbc.NavItem(dcc.Link("🔄 Change Dataset", href="/", className="nav-link"))
        ],
        brand="Credit-to-GDP Analysis",
        color="dark",
        dark=True,
        className="mb-4"
    ),
    dbc.Container([
        html.H2("📈 Credit-to-GDP Gap Time Series", className="text-center mt-4"),
        dcc.Dropdown(
            id="country-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False
        ),
        dcc.Graph(id="time-series-graph", style={'height': '700px'})
    ], fluid=True, className="my-4")
])

# 3d. Statistics Page
statistics_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("🏠 Home", href="/preview", className="nav-link")),
            dbc.NavItem(dcc.Link("📈 Time Series", href="/time-series", className="nav-link")),
            dbc.NavItem(dcc.Link("📊 Statistics", href="/statistics", className="nav-link")),
            dbc.NavItem(dcc.Link("📉 Histogram", href="/histogram", className="nav-link")),
            dbc.NavItem(dcc.Link("🔄 Change Dataset", href="/", className="nav-link"))
        ],
        brand="Credit-to-GDP Analysis",
        color="dark",
        dark=True,
        className="mb-4"
    ),
    dbc.Container([
        html.H2("📊 Descriptive Statistics of Credit-to-GDP Gap", className="text-center mt-4"),
        dcc.Dropdown(
            id="state-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False
        ),
        dash_table.DataTable(
            id='desc-table',
            style_table={'overflowX': 'auto', 'width': '100%'},
            style_cell={'textAlign': 'left'}
        )
    ], fluid=True, className="my-4")
])

# 3e. Histogram Page
histogram_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("🏠 Home", href="/preview", className="nav-link")),
            dbc.NavItem(dcc.Link("📈 Time Series", href="/time-series", className="nav-link")),
            dbc.NavItem(dcc.Link("📊 Statistics", href="/statistics", className="nav-link")),
            dbc.NavItem(dcc.Link("📉 Histogram", href="/histogram", className="nav-link")),
            dbc.NavItem(dcc.Link("🔄 Change Dataset", href="/", className="nav-link"))
        ],
        brand="Credit-to-GDP Analysis",
        color="dark",
        dark=True,
        className="mb-4"
    ),
    dbc.Container([
        html.H2("📉 Histogram of Daily Changes in Credit-to-GDP Gap", className="text-center mt-4"),
        dcc.Dropdown(
            id="histogram-dropdown",
            options=dropdown_options,
            value='all',
            clearable=False
        ),
        dcc.Graph(id="histogram-graph", style={'height': '700px', 'width': '95%'})
    ], fluid=True, className="my-4")
])

# ---------------------------
# 4. Callbacks
# ---------------------------
# Callback to update the selected dataset and navigate to preview page when Proceed is clicked
@app.callback(
    Output('url', 'pathname'),
    Output('selected-dataset', 'data'),
    Input('proceed-button', 'n_clicks'),
    State('group-dropdown', 'value')
)
def update_dataset(n_clicks, selected_group):
    if n_clicks:
        return '/preview', selected_group
    return dash.no_update, dash.no_update

# Callback to render pages based on URL and selected dataset
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('selected-dataset', 'data')
)
def display_page(pathname, selected_dataset):
    # Load dataset based on selected group
    if selected_dataset not in DATA_GROUPS:
        selected_dataset = DEFAULT_DATASET
    df = load_data(DATA_GROUPS[selected_dataset])
    global df_preview, dropdown_options
    df_preview = df.head(10).copy().round(2)  # Change this number to display more rows
    countries = sorted(df['BORROWERS_CTY'].unique())
    dropdown_options = [{'label': 'All countries', 'value': 'all'}] + [{'label': c, 'value': c} for c in countries]

    if pathname == '/time-series':
        return time_series_layout
    elif pathname == '/statistics':
        return statistics_layout
    elif pathname == '/histogram':
        return histogram_layout
    elif pathname == '/preview':
        return home_layout
    else:
        return selection_layout

# Callback for Time Series Graph
@app.callback(
    Output("time-series-graph", "figure"), 
    Input("country-dropdown", "value"),
    State('selected-dataset', 'data')
)
def update_line_chart(selected_state, selected_dataset):
    df = load_data(DATA_GROUPS[selected_dataset])
    if selected_state == 'all':
        filtered_df = df
    else:
        filtered_df = df[df['BORROWERS_CTY'] == selected_state]
    
    fig = px.line(
        filtered_df, 
        x="TIME_PERIOD", 
        y="OBS_VALUE", 
        color="BORROWERS_CTY",
        title="Credit-to-GDP Gap Time Series",
        labels={"TIME_PERIOD": "Year", "OBS_VALUE": "Credit-to-GDP Gap", "BORROWERS_CTY": "Country"}
    )
    return fig

# Callback for Statistics Table
@app.callback(
    Output('desc-table', 'data'),
    Output('desc-table', 'columns'),
    Input('state-dropdown', 'value'),
    State('selected-dataset', 'data')
)
def update_table(selected_state, selected_dataset):
    df = load_data(DATA_GROUPS[selected_dataset])
    if selected_state == 'all':
        desc_stats = df['OBS_VALUE'].describe().reset_index()
    else:
        desc_stats = df[df['BORROWERS_CTY'] == selected_state]['OBS_VALUE'].describe().reset_index()
    
    desc_stats.columns = ['Statistic', 'Value']
    return desc_stats.to_dict('records'), [{"name": col, "id": col} for col in desc_stats.columns]

# Callback for Histogram
@app.callback(
    Output("histogram-graph", "figure"), 
    Input("histogram-dropdown", "value"),
    State('selected-dataset', 'data')
)
def update_histogram(selected_state, selected_dataset):
    df = load_data(DATA_GROUPS[selected_dataset])
    if selected_state == 'all':
        filtered_df = df
    else:
        filtered_df = df[df['BORROWERS_CTY'] == selected_state]

    fig = px.histogram(
        filtered_df, 
        x="DAILY_CHANGE", 
        nbins=50,
        title=f"Histogram of Daily Changes in Credit-to-GDP Gap ({selected_state})",
        labels={"DAILY_CHANGE": "Daily Change in Credit-to-GDP Gap"},
        color_discrete_sequence=["#636EFA"]
    )
    return fig

# ---------------------------
# 5. Run App
# ---------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
