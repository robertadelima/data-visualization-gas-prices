import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# from shapely.geometry import Point

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

def options_from_iterable(iterable):
    return [{ "label": str(option),
              "value": str(option) }
            for option in iterable]

def values_from_iterable(iterable):
    return {str(option): str(option)
            for option in iterable}

# --------------------

cities_map = html.Div([
    dcc.Graph(id='brazil_map', figure={}),
], className='brazil-map')

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
                                    html.H4(id="places_badge_count", className="card-text"),
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
                                    html.H6("Preços analisados", className="card-title"),
                                    html.H4(id="prices_badge_count", className="card-text"),
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
                                    html.H6("Meses selecionados", className="card-title"),
                                    html.H4(id="months_badge_count", className="card-text"),
                            ]
                            ),
                        ], className="card"
                    )
                ]))
            ], className="cards-row",
        ),
],)

filters = html.Div([
    html.Br(),
    html.H5("Locais selecionados:",
        className="dcc_control"
    ),
    dcc.Dropdown(id="selected_places",
            options=[{ "label": PLACES_DICT[place_id],
                       "value": place_id }
                     for place_id in PLACES_DICT],
            multi=True,
            value=['city_MANAUS', 'city_BRASILIA', 'city_FLORIANOPOLIS', 'city_SALVADOR', 'city_SAO PAULO'],
            className="dcc_control",
            ),
    html.Br(),
    html.H5("Combustível selecionado:",
        className="dcc_control"
    ),
    dcc.RadioItems(
        id="selected_product",
        options=options_from_iterable(PRODUCTS),
        value='GASOLINA COMUM',
        labelStyle={'display': 'inline-block', 'margin':'4px'},
        className="dcc_control",
    ),
], className='filters-div')


date_slider = html.Div([
    html.Div([
        html.H5("Período selecionado:"),
    ]),
    dcc.RangeSlider(
        id="selected_years",
        min=min(YEARS),
        max=max(YEARS),
        value=(2018, max(YEARS)),
        marks=values_from_iterable(YEARS),
        className="dcc_control",
    ),
], className="slider_control")

header_section = html.Div([
    html.Header([
        html.Div([
            html.H1('Preços dos Combustíveis no Brasil'),
            html.H6('Última atualização: 20/06/2020'),
        ], className="header-title")
    ], className="header-div")
])
data_selection_section = html.Div([
    cities_map,
    html.Div([
        info_badges,
        filters,
    ], className="filters")
], className="map-and-filters")

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

def build_brazil_map_figure(filtered_dataset, selected_product):
    return px.scatter_mapbox(filtered_dataset,
                             lat=COLUMNS.LATITUDE, lon=COLUMNS.LONGITUDE,
                             size=COLUMNS.MARKET_PRICE_MEAN,
                             width=800, height=600,
                             zoom=2.5, # mapbox_style="dark",
                             center=dict(lat=-11.619893, lon=-56.408030),
                             color_continuous_scale=px.colors.sequential.Aggrnyl,
                             color=COLUMNS.MARKET_PRICE_MEAN,
                             hover_name=COLUMNS.PLACE_NAME,
                             hover_data={ COLUMNS.MARKET_PRICE_MEAN: ':.2f',
                                          COLUMNS.LATITUDE: False,
                                          COLUMNS.LONGITUDE: False },
                             title=f"Preço Médio do Combustível nas Revendas { PRODUCT_UNITS[selected_product] }",
    ) 

"""#def get_polygon(filtered_dataset, color='blue'):
def get_polygon(lons, lats, color='blue'):
    #lons = filtered_dataset['Lon'].tolist()[:5]
    #lats = filtered_dataset['Lat'].tolist()[:5]
    print(type(lons[1]))
    geojd = {"type": "FeatureCollection"}
    geojd['features'] = []
    coords = []
    for lon, lat in zip(lons, lats): 
        coords.append((lon, lat))   
    #coords.append((lons[0], lats[0]))  #close the polygon  
    geojd['features'].append({ "type": "Feature",
                               "geometry": {"type": "Polygon",
                                            "coordinates": [coords] }})
    print(coords)
    layer=dict(sourcetype = 'geojson',
             source = geojd,
             below ='',  
             type = 'fill',   
             color = color,
             opacity = 0.2)
    return layer 

def build_brazil_map_figure(filtered_dataset):
    fig = go.Figure(go.Scattermapbox(
                        lat=filtered_dataset[COLUMNS.LATITUDE],
                        lon=filtered_dataset[COLUMNS.LONGITUDE],
                        mode='markers',
                        text=filtered_dataset[COLUMNS.MARKET_PRICE_MEAN],
    ))
    fig.update_layout(mapbox_style="open-street-map",
        hovermode='closest',
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=-11.619893,
                lon=-56.408030
            ),
        pitch=0,
        zoom=2.5
        )
    )
    mylayers = []
    filtered_with_polygons = merge_places_polygons_data(filtered_dataset)
    mylayers.append(get_polygon(lats=[-29.081636, -28.208320, -27.005862, -26.237557, -26.196977], lons=[-49.620587, -50.480014, -53.374927, -53.510626, -48.761160],  color='gold'))
    #mylayers.append(get_polygon(lats=[-28.61117903, -28.61112627, -28.54095732, -28.44592555, -27.84035526], lons=[-48.82158597, -48.82227018, -48.757575, -48.7096376, -48.50136667],  color='gold'))
    #mylayers.append(get_polygon(filtered_dataset, color='gold'))
    
    fig.layout.update(mapbox_layers = mylayers); 
    return fig"""


def build_market_price_plot(filtered_dataset, selected_product):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_PRICE_MEAN,
                   line_group=COLUMNS.PLACE_NAME,
                   hover_data = ['UNIDADE DE MEDIDA'],
                   color=COLUMNS.PLACE_NAME,
                   title=f"Preço Médio nas Revendas { PRODUCT_UNITS[selected_product] }")

def build_market_margin_plot(filtered_dataset, selected_product):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_MARGIN,
                   line_group=COLUMNS.PLACE_NAME,
                   color=COLUMNS.PLACE_NAME,
                   title=f"Margem Média das Revendas { PRODUCT_UNITS[selected_product] }")

def build_market_price_std_deviation_plot(filtered_dataset, selected_product):
    return px.bar(filtered_dataset,
                   x=COLUMNS.PLACE_NAME,
                   y=COLUMNS.MARKET_PRICE_STD,
                   barmode='group',
                   color='ANO',
                   title=f"Desvio Padrão Médio dos Preços nas Revendas { PRODUCT_UNITS[selected_product] }",
                   color_continuous_scale=px.colors.cyclical.IceFire)

def build_market_price_var_coef_plot(filtered_dataset, selected_product):
    return px.bar(filtered_dataset,
                   x=COLUMNS.PLACE_NAME,
                   y=COLUMNS.MARKET_PRICE_VAR_COEF,
                   barmode='group',
                   color='ANO',
                   title=f"Coeficiente de Variação Médio dos Preços nas Revendas { PRODUCT_UNITS[selected_product] }",
                   color_continuous_scale=px.colors.cyclical.IceFire)

def filter_by_places(dataset, selected_places):
    '''
    Returns a dataset with data matching
    any of the selected places
    '''
    if type(selected_places) is not list:
        selected_places = [selected_places]

    cities = []
    states = []
    regions = []

    for place_id in selected_places:
        if place_id.startswith('city'):
            cities.append(PLACES_DICT[place_id])
        elif place_id.startswith('state'):
            states.append(PLACES_DICT[place_id])
        elif place_id.startswith('region'):
            regions.append(PLACES_DICT[place_id])
        else:
            raise Exception(place_id)

    cities_filter = ((dataset[COLUMNS.PLACE_TYPE] == 'CIDADE') &
                     (dataset[COLUMNS.PLACE_NAME].isin(cities)))
    states_filter = ((dataset[COLUMNS.PLACE_TYPE] == 'ESTADO') &
                     (dataset[COLUMNS.PLACE_NAME].isin(states)))
    regions_filter = ((dataset[COLUMNS.PLACE_TYPE] == 'REGIAO') &
                     (dataset[COLUMNS.PLACE_NAME].isin(regions)))

    filters = cities_filter | states_filter | regions_filter

    return dataset[filters]

def get_gas_stations_count(dataset):
    #print(dataset)
    #print(len(dataset))
    #print(len(dataset.dropna()))
    '''
    Computes the real gas station total count,
    removing duplicates from compound places
    (one place inside the other)
    '''

    cities_data = dataset[dataset[COLUMNS.PLACE_TYPE] == 'CIDADE'].dropna()
    states_data = dataset[dataset[COLUMNS.PLACE_TYPE] == 'ESTADO'].dropna()
    regions_data = dataset[dataset[COLUMNS.PLACE_TYPE] == 'REGIAO'].dropna()

    #DATASET[DATASET['ESTADO'] == states_data['NOME DO LOCAL']]['REGIÃO']
    #states_data['REGION'] = DATASET[DATASET['ESTADO'] == states_data['NOME DO LOCAL']]['REGIÃO']

    count_from_regions = regions_data[COLUMNS.GAS_STATION_COUNT].sum()

    #cities_list = cities_data['MUNICÍPIO'].unique()
    states_list = states_data['NOME DO LOCAL'].unique() #SE NOME DO LOCAL É UM ESTADO, NÃO TEM MAIS "ESTADO" E "REGIAÕ"
    regions_list = regions_data['NOME DO LOCAL'].str.replace('REGIAO ', '').unique() #SE NOME DO LOCAL É UMA REGIAO, NÃO TEM MAIS "ESTADO" E "REGIAÕ"

    #@np.vectorize
    def is_under_selected_region(state):
        if(type(state) is float):
            return true
        dataset_match_row = DATASET[DATASET['ESTADO'] == state].tail(1)
        return dataset_match_row['REGIÃO'].isin(regions_list)

    #print((states_data['NOME DO LOCAL']).dtype)

    count_from_states = states_data[~(states_data['NOME DO LOCAL'].apply(is_under_selected_region))][COLUMNS.GAS_STATION_COUNT].sum() if len(states_data) > 0 else 0
    count_from_cities = cities_data.loc[(~cities_data['ESTADO'].isin(states_list)) & (~cities_data['REGIÃO'].isin(regions_list))][COLUMNS.GAS_STATION_COUNT].sum()
   

    return sum([count_from_cities, count_from_states, count_from_regions])
    #foreach cities_data, if cities_data['ESTADO'] in states_list, set qtd = 0
    #foreach states_data, if states_data['REGIÃO'] in regions_list, set qtd = 0

    '''count_from_regions = regions_data[COLUMNS.GAS_STATION_COUNT].sum()

    # SOMA TODOS AS REGIÕES, FAZ UMA LISTA DE REGIÕES UNICAS FILTRADAS
    # VERIFICA O DATASET PELOS ESTADOS -> SE A REGIÃO ESTIVER NA LISTA, SETA PRA ZERO
    # VERIFICA O DATASET PELOS CIDADES -> 

    count_from_states = states_data[COLUMNS.GAS_STATION_COUNT].sum()
    count_from_cities = cities_data[COLUMNS.GAS_STATION_COUNT].sum()

    @np.vectorize
    # PARANA, 100, ESTADO
    # SUL, 1000, REGIAO
    def withdraw_city_counts(place_name, place_gas_station_count, place_column):
        ''''''
        For each place, withdraw the sum of the
        gas station counts of the cities within the place.
        ''''''
        cd = cities_data
        city_within_place_filter = cd[place_column] == place_name
        # print(f'place_column={place_column}, place_name={place_name}')
        cities_within_place_data = cd[city_within_place_filter]
        # print('city_within_place_data')
        # print(cities_within_place_data)
        cities_gas_station_counts = cities_within_place_data[COLUMNS.GAS_STATION_COUNT]
        # print('cities_gas_station_counts')
        # print(cities_gas_station_counts)

        return place_gas_station_count - cities_gas_station_counts.sum()

    count_from_states = 0
    if len(states_data) > 0:
        counts_by_state = states_data.groupby(COLUMNS.PLACE_NAME, as_index=False).sum()
        count_from_states = \
            withdraw_city_counts(counts_by_state[COLUMNS.PLACE_NAME],
                                counts_by_state[COLUMNS.GAS_STATION_COUNT],
                                COLUMNS.STATE)\
                                .sum()

    @np.vectorize
    # SUDESTE, 1000, REGIAO
    def withdraw_state_counts(place_name, place_gas_station_count, place_column):
        ''''''
        For each place, withdraw the sum of the
        gas station counts of the states within the place.
        ''''''
        sd = states_data
        state_within_place_filter = sd[place_column] == place_name
        # print(f'place_column={place_column}, place_name={place_name}')
        states_within_place_data = sd[state_within_place_filter]
        # print('city_within_place_data')
        # print(cities_within_place_data)
        states_gas_station_counts = states_within_place_data[COLUMNS.GAS_STATION_COUNT]
        # print('cities_gas_station_counts')
        # print(cities_gas_station_counts)

        return place_gas_station_count - states_gas_station_counts.sum()

    count_from_regions = 0
    if len(regions_data) > 0:
        counts_by_region = regions_data.groupby(COLUMNS.PLACE_NAME, as_index=False).sum()

        count_from_regions = \
            withdraw_city_counts(counts_by_region[COLUMNS.PLACE_NAME].str.replace('REGIAO ', ''),
                                counts_by_region[COLUMNS.GAS_STATION_COUNT],
                                COLUMNS.REGION)\
                                .sum()
        count_from_regions += \
            withdraw_state_counts(counts_by_region[COLUMNS.PLACE_NAME].str.replace('REGIAO ', ''),
                                counts_by_region[COLUMNS.GAS_STATION_COUNT],
                                COLUMNS.REGION)\
                                .sum()'''

   

# DATASET.head(1).transpose()

@app.callback(
    [Output(component_id='brazil_map', component_property='figure'),
     Output(component_id='market_price_plot', component_property='figure'),
     Output(component_id='market_margin_plot', component_property='figure'),
     Output(component_id='market_price_std_deviation_plot', component_property='figure'),
     Output(component_id='market_price_coef_var_plot', component_property='figure'),
     Output(component_id='places_badge_count', component_property='children'),
     Output(component_id='prices_badge_count', component_property='children'),
     Output(component_id='months_badge_count', component_property='children'),],
    [Input(component_id='selected_product', component_property='value'),
     Input(component_id='selected_years', component_property='value'),
     Input(component_id='selected_places', component_property='value'),]
)
def update_plots_from_filters(selected_product, selected_year_range, selected_places):
    product_filter = DATASET[COLUMNS.PRODUCT] == selected_product

    dataset_years = DATASET[COLUMNS.MONTH].dt.year
    years_filter = ((dataset_years >= selected_year_range[0]) &
                    (dataset_years <= selected_year_range[1]))

    filtered_dataset = DATASET[product_filter & years_filter]

    filtered_dataset = generate_aggregate_data(filtered_dataset)

    filtered_dataset = filter_by_places(filtered_dataset, selected_places)

    market_price_plot_figure = build_market_price_plot(filtered_dataset, selected_product)
    market_margin_plot_figure = build_market_margin_plot(filtered_dataset, selected_product)

    filtered_dataset['ANO'] = filtered_dataset[COLUMNS.MONTH].dt.year.astype(str)
    place_groups = filtered_dataset.groupby([COLUMNS.PLACE_NAME], as_index=False)
    place_and_year_groups = filtered_dataset.groupby([COLUMNS.PLACE_NAME, 'ANO'], as_index=False)

    brazil_map_figure = build_brazil_map_figure(place_groups.mean(), selected_product)
    market_price_std_deviation_plot = build_market_price_std_deviation_plot(place_and_year_groups.mean(), selected_product)
    market_price_var_coef_plot = build_market_price_var_coef_plot(place_and_year_groups.mean(), selected_product)

    places_badge_count = len(selected_places)
    #prices_badge_count = get_gas_stations_count(filtered_dataset)
    prices_badge_count = filtered_dataset[COLUMNS.GAS_STATION_COUNT].sum() 
    months_badge_count = len(filtered_dataset[COLUMNS.MONTH].unique())

    return (brazil_map_figure,
            market_price_plot_figure,
            market_margin_plot_figure,
            market_price_std_deviation_plot,
            market_price_var_coef_plot,
            places_badge_count,
            prices_badge_count,
            months_badge_count)

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
