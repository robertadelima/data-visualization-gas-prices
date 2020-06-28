import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from data_provider import *

app = dash.Dash(__name__)

with open(".mapbox_token.txt") as map_token_file:
    token = map_token_file.read()
    px.set_mapbox_access_token(token)

# --------------------

def options_from_dict(dictionary):
    return [{ "label": str(dictionary[key]),
              "value": str(key) }
            for key in dictionary]

# --------------------

cities_map = html.Div([
    dcc.Graph(id='brazil_map', figure={}),
], className='brazil_map')

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
], style={'display': 'flex'})
filters = html.Div([
    html.P("Municípios selecionados:",
        className="dcc_control"
    ),
    dcc.Dropdown(id="selected_cities",
            options=options_from_dict(CITIES),
            multi=True,
            value=['218', '459', '408', '73', '287'],
            className="dcc_control",
            ),
    html.P("Combustível selecionado",
        className="dcc_control"
    ),
    dcc.RadioItems(
        id="selected_product",
        options=options_from_dict(PRODUCTS),
        value=3,
        labelStyle={"display": "inline-block"},
        className="dcc_control",
    ),
], style={'display': 'inline-block'})
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
        ], className="header_flag"),
        html.Div([
            html.H1('Preços dos Combustíveis - Santa Catarina, Brasil'),
            html.H4('Última atualização: 20/06/2020'),
        ], className="header_title")
    ])
])
data_selection_section = html.Div([
    cities_map,
    html.Div([
        info_badges,
        filters,
    ], className="filters")
], className="map_and_filters")

plots_section = html.Div([
     dcc.Graph(id='market_price_plot', figure={}),
     dcc.Graph(id='market_margin_plot', figure={})
])

# Generate the app
app.layout = html.Div([
    header_section,
    data_selection_section,
    date_slider,
    plots_section,
])

def build_brazil_map_figure(filtered_dataset):
    return px.scatter_mapbox(filtered_dataset,
                             lat=COLUMNS.LATITUDE, lon=COLUMNS.LONGITUDE,
                             size=COLUMNS.MARKET_PRICE_MEAN,
                             width=800, height=600, zoom=3, mapbox_style="open-street-map",
                             center=dict(lat=-11.619893, lon=-56.408030),
                             color_continuous_scale=px.colors.cyclical.IceFire)

def build_market_price_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_PRICE_MEAN,
                   line_group=COLUMNS.CITY,
                   color=COLUMNS.CITY)

def build_market_margin_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_MARGIN,
                   line_group=COLUMNS.CITY,
                   color=COLUMNS.CITY)

@app.callback(
    [Output(component_id='brazil_map', component_property='figure'),
     Output(component_id='market_price_plot', component_property='figure'),
     Output(component_id='market_margin_plot', component_property='figure')],
    [Input(component_id='selected_cities', component_property='value'),
    Input(component_id='selected_product', component_property='value')]
)
def update_plots_from_filters(selected_cities, selected_product):

    if type(selected_cities) is not list:
        selected_cities = [selected_cities]

    selected_product_name = PRODUCTS[int(selected_product)]
    product_filter = DATASET[COLUMNS.PRODUCT] == selected_product_name

    selected_cities_names = [CITIES[int(city)] for city in selected_cities]
    cities_filter = DATASET[COLUMNS.CITY_NAME].isin(selected_cities_names)

    filtered_dataset = DATASET[product_filter & cities_filter]

    brazil_map_figure = build_brazil_map_figure(filtered_dataset)
    market_price_plot_figure = build_market_price_plot(filtered_dataset)
    market_margin_plot_figure = build_market_margin_plot(filtered_dataset)

    return (brazil_map_figure,
            market_price_plot_figure,
            market_price_plot_figure)

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
