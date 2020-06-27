import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from data_provider import *

df = DATASET

app = dash.Dash(__name__)

# --------------------

def options_from_dict(dictionary):
    return [{ "label": str(dictionary[key]),
              "value": str(key) }
            for key in dictionary]

# --------------------

cities_map = html.Div([
    dcc.Dropdown(id="selected_cities",
                 options=options_from_dict(CITIES),
                 multi=True,
                 value=1,
                 style={'width': "60%"}
                 ),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='brazil_map', figure={}),
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
],style={'display': 'flex'}
)
county_options = [
]
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
        options=options_from_dict(CITIES),
        multi=True,
        value=[],
        className="dcc_control",
    ),
    html.P("Combustível selecionado",
        className="dcc_control"
    ),
    dcc.RadioItems(
        id="selected_product",
        options=options_from_dict(PRODUCTS),
        value=0,
        labelStyle={"display": "inline-block"},
        className="dcc_control",
    ),
],style={'display': 'inline-block'}
)
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
    html.Header([
        html.Div([
            html.Img(src=app.get_asset_url('bandeira-sc.jpg'), style={'width':'30%'})
        ], className="flag"),
        html.Div([
            html.H1('Preços dos Combustíveis - Santa Catarina, Brasil'),
            html.H4('Última atualização: 20/06/2020'),
        ], className="header_title")
    ])
])
data_selection_section = html.Div([
    cities_map,
    info_badges,
    filters,
    date_slider,
])
plots_section = html.Div([
     dcc.Graph(id='market_price_mean_graph', figure={})
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
     Output(component_id='brazil_map', component_property='figure'),
     Output(component_id='market_price_mean_graph', component_property='figure')
     ],
    [Input(component_id='selected_cities', component_property='value'),
    Input(component_id='selected_product', component_property='value')]
)
    # Plotly Express
def update_graph(selected_cities, selected_product):
    if not isinstance(selected_cities, list): selected_cities = [selected_cities]
    nomes_cidades = [CITIES[int(cidade)] for cidade in selected_cities]
    container = "Região selecionada: {} Produto selecionado: {}".format(nomes_cidades, selected_product)

    dff = df.copy()
    dff = dff[dff[COLUMNS.CITY_NAME].isin(nomes_cidades)]
    dff = dff[dff[COLUMNS.PRODUCT] == PRODUCTS[int(selected_product)]]

    px.set_mapbox_access_token(open(".mapbox_token.txt").read())
    fig = px.scatter_mapbox(dff, lat=COLUMNS.LATITUDE, lon=COLUMNS.LONGITUDE, color_continuous_scale=px.colors.cyclical.IceFire, 
        zoom=3, size=COLUMNS.MARKET_PRICE_MEAN, width=1000, height=800, mapbox_style="open-street-map",
        center=dict(lat=-11.619893, lon=-56.408030))
    
    dfff = dff.groupby([COLUMNS.MONTH, COLUMNS.CITY])[COLUMNS.MARKET_PRICE_MEAN].apply(list)

    fig2 = px.line(dff, x=COLUMNS.MONTH, y=COLUMNS.MARKET_PRICE_MEAN, line_group=COLUMNS.CITY, color=COLUMNS.CITY)
    return container, fig , fig2

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
