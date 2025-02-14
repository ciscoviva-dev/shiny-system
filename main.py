import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import urllib.request
import certifi

# Load dataset from URL
url = 'https://catalogue.data.govt.nz/dataset/4df114b8-5995-49e3-85df-185c7a30cf12/resource/0f3cbea0-57ac-4ac9-a89d-024c453e6947/download/gmp-quarterly-dashboard-dataset-csv.csv'
response = urllib.request.urlopen(url, cafile=certifi.where())
df = pd.read_csv(response)

# Convert Quarter to datetime
df['Quarter'] = pd.to_datetime(df['Quarter'], errors='coerce')

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GMP Dashboard"

def create_dropdown(id, label, options):
    return dbc.Col([
        html.Label(label, className="fw-bold"),
        dcc.Dropdown(id=id, options=[{"label": i, "value": i} for i in options], 
                     multi=True, placeholder=f"Select {label}")
    ], md=4)

filters = dbc.Row([
    create_dropdown("year-filter", "Year", df['Year'].unique()),
    create_dropdown("region-filter", "Region", df['Region'].unique()),
    create_dropdown("category-filter", "Category", df['Category'].unique())
])

tabs = dbc.Tabs([
    dbc.Tab(label='Overview', tab_id='tab-overview'),
    dbc.Tab(label='Regional Analysis', tab_id='tab-regional'),
    dbc.Tab(label='Venues & Machines', tab_id='tab-venues'),
    dbc.Tab(label='Socioeconomic Impact', tab_id='tab-socio')
], id='tabs', active_tab='tab-overview')

app.layout = dbc.Container([
    html.H1("GMP Dashboard", className="text-center mt-4"),
    filters,
    tabs,
    html.Div(id='tab-content', className='mt-4')
])

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'active_tab'),
    Input('year-filter', 'value'),
    Input('region-filter', 'value'),
    Input('category-filter', 'value')
)
def update_tab(tab, selected_years, selected_regions, selected_categories):
    dff = df.copy()
    if selected_years:
        dff = dff[dff['Year'].isin(selected_years)]
    if selected_regions:
        dff = dff[dff['Region'].isin(selected_regions)]
    if selected_categories:
        dff = dff[dff['Category'].isin(selected_categories)]
    
    if tab == 'tab-overview':
        fig1 = px.line(dff, x='Quarter', y='GMP', color='Region', template="plotly_dark")
        fig2 = px.bar(dff, x='Year', y='GMP', color='Region', template="plotly_dark")
        fig3 = px.scatter(dff, x='GMP', y='Venues', color='Region', template="plotly_dark")
        fig4 = px.box(dff, x='Region', y='GMP', template="plotly_dark")
        
        return dbc.Row([
            dbc.Col(dcc.Graph(figure=fig1), md=6),
            dbc.Col(dcc.Graph(figure=fig2), md=6),
            dbc.Col(dcc.Graph(figure=fig3), md=6),
            dbc.Col(dcc.Graph(figure=fig4), md=6)
        ])
    return html.P("Select a tab to view data.")

if __name__ == '__main__':
    app.run_server(debug=True)
