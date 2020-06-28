import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from data_provider import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
    dbc.Row(
            [
                dbc.Col(html.Div([
                    dbc.Card(
                        [
                            dbc.CardHeader(dbc.CardImg(src="/assets/places-icon.png", top=True, className='card-icons')),
                            dbc.CardBody(
                                [
                                    html.H6("Locais escolhidos", className="card-title"),
                                    html.H2(id="places_badge_count", className="card-text"),
                            ]
                            )
                        ]
                    )
                ])),
                dbc.Col(html.Div([
                    dbc.Card(
                        [
                            dbc.CardHeader(dbc.CardImg(src="/assets/price-icon.png", top=True, className='card-icons')),
                            dbc.CardBody(
                                [
                                    html.H6("Preços aferidos", className="card-title"),
                                    html.H2(id="prices_badge_count", className="card-text"),
                            ]
                            ),
                        ],
                    )
                ])),
                dbc.Col(html.Div([
                    dbc.Card(
                        [
                            dbc.CardHeader(dbc.CardImg(src="/assets/months-icon.png", top=True, className='card-icons')),
                            dbc.CardBody(
                                [
                                    html.H6("Meses analisados", className="card-title"),
                                    html.H2(id="months_badge_count", className="card-text"),
                            ]
                            ),
                        ],
                    )
                ]))
            ], style={'padding':'20px'}
        ), 
],)

filters = html.Div([
    html.Br(),
    html.H5("Locais selecionados:",
        className="dcc_control"
    ),
    dcc.Dropdown(id="selected_cities",
            options=options_from_dict(CITIES),
            multi=True,
            value=['218', '459', '408', '73', '287'],
            className="dcc_control",
            ),
    html.Br(),
    html.H5("Combustível selecionado:",
        className="dcc_control"
    ),
    dcc.RadioItems(
        id="selected_product",
        options=options_from_dict(PRODUCTS),
        value=3,
        labelStyle={"display": "inline-block"},
        className="dcc_control",
    ),
], style={'display': 'inline-block', 'padding': '20px'})


date_slider = html.Div([
    html.Div([
        html.H2(min(YEARS)),
        html.H2(max(YEARS),
                style={'float': 'right', 'vertical-align': 'top'}),
    ]),
    dcc.RangeSlider(
        id="selected_years",
        min=min(YEARS),
        max=max(YEARS),
        value=(min(YEARS), max(YEARS)),
        className="dcc_control",
    ),
])

header_section = html.Div([
    html.Header([
        html.Div([
            html.H1('Preços dos Combustíveis no Brasil'),
            html.H6('Última atualização: 20/06/2020'),
        ], className="header_title")
    ], className="header_div")
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
     dcc.Graph(id='market_margin_plot', figure={}),
     dbc.Row(
            [
                dbc.Col(html.Div([
                            dcc.Graph(id='market_price_std_deviation_plot', figure={}),
                ])),
                dbc.Col(html.Div([
                            dcc.Graph(id='market_price_coef_var_plot', figure={}),
                ]))
            ])
])

# Generate the app
app.layout = html.Div([
    header_section,
    data_selection_section,
    date_slider,
    plots_section
])

def build_brazil_map_figure(filtered_dataset):
    return px.scatter_mapbox(filtered_dataset,
                             lat=COLUMNS.LATITUDE, lon=COLUMNS.LONGITUDE,
                             size=COLUMNS.MARKET_PRICE_MEAN,
                             width=700, height=550, zoom=3, mapbox_style="open-street-map",
                             center=dict(lat=-11.619893, lon=-56.408030),
                             color_continuous_scale=px.colors.cyclical.IceFire,
                             color=COLUMNS.MARKET_PRICE_MEAN,
                             title="Preço Médio do Combustível nas Revendas")

def build_market_price_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_PRICE_MEAN,
                   line_group=COLUMNS.CITY,
                   color=COLUMNS.CITY,
                   title="Margem Média das Revendas")

def build_market_margin_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_MARGIN,
                   line_group=COLUMNS.CITY,
                   color=COLUMNS.CITY)

def build_market_price_std_deviation_plot(filtered_dataset):
    return px.bar(filtered_dataset,
                   x=COLUMNS.CITY,
                   y=COLUMNS.MARKET_PRICE_STD,
                   barmode='group',
                   color='ANO',
                   title='Desvio Padrão Médio dos Preços nas Revendas')

def build_market_price_var_coef_plot(filtered_dataset):
    return px.bar(filtered_dataset,
                   x=COLUMNS.CITY,
                   y=COLUMNS.MARKET_PRICE_VAR_COEF,
                   barmode='group',
                   color='ANO',
                   title='Coeficiente de Variação Médio dos Preços nas Revendas')

@app.callback(
    [Output(component_id='brazil_map', component_property='figure'),
     Output(component_id='market_price_plot', component_property='figure'),
     Output(component_id='market_margin_plot', component_property='figure'),
     Output(component_id='market_price_std_deviation_plot', component_property='figure'),
     Output(component_id='market_price_coef_var_plot', component_property='figure'),
     Output(component_id='places_badge_count', component_property='children'),
     Output(component_id='prices_badge_count', component_property='children'),
     Output(component_id='months_badge_count', component_property='children')],
    [Input(component_id='selected_cities', component_property='value'),
    Input(component_id='selected_product', component_property='value'),
    Input(component_id='selected_years', component_property='value')
    ]
)
def update_plots_from_filters(selected_cities, selected_product, selected_year_range):

    if type(selected_cities) is not list:
        selected_cities = [selected_cities]

    selected_product_name = PRODUCTS[int(selected_product)]
    product_filter = DATASET[COLUMNS.PRODUCT] == selected_product_name

    selected_cities_names = [CITIES[int(city)] for city in selected_cities]
    cities_filter = DATASET[COLUMNS.CITY_NAME].isin(selected_cities_names)

    dataset_years = DATASET[COLUMNS.MONTH].dt.year
    years_filter = ((dataset_years >= selected_year_range[0]) &
                    (dataset_years <= selected_year_range[1]))

    filtered_dataset = DATASET[product_filter &
                               cities_filter &
                               years_filter]
    
    filtered_dataset_grouped_by_year = filtered_dataset.groupby([
                                        filtered_dataset[COLUMNS.CITY], 
                                        filtered_dataset[COLUMNS.MONTH].dt.year]).mean()
    filtered_dataset_grouped_by_year = filtered_dataset_grouped_by_year.reset_index()
    filtered_dataset_grouped_by_year.rename(columns={'MÊS': 'ANO'}, inplace=True)

    brazil_map_figure = build_brazil_map_figure(filtered_dataset)
    market_price_plot_figure = build_market_price_plot(filtered_dataset)
    market_margin_plot_figure = build_market_margin_plot(filtered_dataset)
    market_price_std_deviation_plot = build_market_price_std_deviation_plot(filtered_dataset_grouped_by_year)
    market_price_var_coef_plot = build_market_price_var_coef_plot(filtered_dataset_grouped_by_year)

    places_badge_count = len(selected_cities)
    prices_badge_count = filtered_dataset[COLUMNS.GAS_STATION_COUNT].sum()
    months_badge_count = len(filtered_dataset[COLUMNS.MONTH].unique())

    return (brazil_map_figure,
            market_price_plot_figure,
            market_price_plot_figure,
            market_price_std_deviation_plot,
            market_price_var_coef_plot,
            places_badge_count,
            prices_badge_count,
            months_badge_count)

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
