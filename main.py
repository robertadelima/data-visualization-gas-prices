import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from data_provider import DATASET, COLUMNS

df = DATASET
print(df.head(3))

app = dash.Dash(__name__)

cities_map = html.Div([
    dcc.Dropdown(id="regiao_selecionada",
                 options=[
                     {"label": "SC", "value": "SC"},
                     {"label": "RS", "value": "RS"},
                     {"label": "PR", "value": "PR"},
                     {"label": "SP", "value": "SP"},
                     {"label": "RJ", "value": "RJ"},],
                 multi=True,
                 value="SC",
                 style={'width': "40%"}
                 ),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='brazil_map', figure={})
])

info_badges = html.Div([
    html.Div([
        html.P("Total de municípios selecionados",
            id="cities_badge_label"),
        html.H6("4",
            id="cities_badge_count")
    ], className="badge"),
    html.Div([
        html.P("Total de preços aferidos",
            id="prices_badge_label"),
        html.H6("1578",
            id="prices_badge_count")
    ], className="badge"),
    html.Div([
        html.P("Total de meses analisados",
            id="months_badge_label"),
        html.H6("60",
            id="months_badge_count")
    ], className="badge"),
])

filters = html.Div([
    html.P("Municípios selecionados:",
        className="dcc_control"
    ),
    dcc.Checklist(
        id="all_cities_checkbox",
        options=[{"label": "Todos", "value": "all"}],
        className="dcc_control",
        value=[],
        style={'text-align': 'right'},
    ),
    dcc.Dropdown(
        id="selected_cities_dropdown",
        options=[
            {"label": "Itajaí", "value": "itj"},
            {"label": "Ilhota", "value": "ilh"},
        ],
        multi=True,
        value=[],
        className="dcc_control",
    ),
    html.P("Combustível selecionado",
        className="dcc_control"
    ),
    dcc.RadioItems(
        id="selected_fuel_radio",
        options=[
            {"label": "Gasolina comum", "value": "gasolina"},
            {"label": "GLP", "value": "glp"},
        ],
        value="gasolina",
        labelStyle={"display": "inline-block"},
        className="dcc_control",
    ),
])
date_slider = html.Div([
    html.H2("2013"),
    dcc.RangeSlider(
        id="year_slider",
        min=2013,
        max=2020,
        value=[2013, 2020],
        className="dcc_control",
    ),
    html.H2("2020"),
])

header_section = html.Div([
    html.Div([
        html.Img(src=app.get_asset_url('bandeira-sc.jpg'))
    ]),
    html.Div([
        html.H1('Preços dos Combustíveis - Santa Catarina, Brasil',
                style={
                    'text-align': 'left',
                }),
        html.H4('Última atualização: 20/06/2020',
                style={
                    'text-align': 'left',
                }),
    ])
])
data_selection_section = html.Div([
    cities_map,
    info_badges,
    filters,
    date_slider,
])
plots_section = html.Div([
])

# Generate the app
app.layout = html.Div([
    header_section,
    data_selection_section,
    plots_section,
])

# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='brazil_map', component_property='figure')],
    [Input(component_id='regiao_selecionada', component_property='value')]
)
    # Plotly Express
def update_graph(opcao_selecionada):

    container = "Região selecionada: {}".format(opcao_selecionada)
    if not isinstance(opcao_selecionada, list): opcao_selecionada = [opcao_selecionada]

    dff = df.copy()
    dff = dff[dff["UF"].isin(opcao_selecionada)]

    px.set_mapbox_access_token(open(".mapbox_token.txt").read())
    fig = px.scatter_mapbox(dff, lat="LATITUDE", lon="LONGITUDE", color_continuous_scale=px.colors.cyclical.IceFire, 
        size_max=30, zoom=5)
    return container, fig

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
