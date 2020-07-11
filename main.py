import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shapely.geometry import Point

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
                                    html.H6("Preços analisados", className="card-title"),
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
                                    html.H6("Meses selecionados", className="card-title"),
                                    html.H2(id="months_badge_count", className="card-text"),
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
            value=['state_SANTA CATARINA', 'city_ITAJAI'],
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
        value=(min(YEARS), max(YEARS)),
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

def build_brazil_map_figure(filtered_dataset):
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
                             title="Preço Médio do Combustível nas Revendas",
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


def build_market_price_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_PRICE_MEAN,
                   line_group=COLUMNS.PLACE_NAME,
                   color=COLUMNS.PLACE_NAME,
                   title="Margem Média das Revendas")

def build_market_margin_plot(filtered_dataset):
    return px.line(filtered_dataset,
                   x=COLUMNS.MONTH,
                   y=COLUMNS.MARKET_MARGIN,
                   line_group=COLUMNS.PLACE_NAME,
                   color=COLUMNS.PLACE_NAME)

def build_market_price_std_deviation_plot(filtered_dataset):
    return px.bar(filtered_dataset,
                   x=COLUMNS.PLACE_NAME,
                   y=COLUMNS.MARKET_PRICE_STD,
                   barmode='group',
                   color='ANO',
                   title='Desvio Padrão Médio dos Preços nas Revendas',
                   color_continuous_scale=px.colors.cyclical.IceFire)

def build_market_price_var_coef_plot(filtered_dataset):
    return px.bar(filtered_dataset,
                   x=COLUMNS.PLACE_NAME,
                   y=COLUMNS.MARKET_PRICE_VAR_COEF,
                   barmode='group',
                   color='ANO',
                   title='Coeficiente de Variação Médio dos Preços nas Revendas',
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

    market_price_plot_figure = build_market_price_plot(filtered_dataset)
    market_margin_plot_figure = build_market_margin_plot(filtered_dataset)

    filtered_dataset['ANO'] = filtered_dataset[COLUMNS.MONTH].dt.year.astype(str)
    place_groups = filtered_dataset.groupby([COLUMNS.PLACE_NAME], as_index=False)
    place_and_year_groups = filtered_dataset.groupby([COLUMNS.PLACE_NAME, 'ANO'], as_index=False)

    brazil_map_figure = build_brazil_map_figure(place_groups.mean())
    market_price_std_deviation_plot = build_market_price_std_deviation_plot(place_and_year_groups.mean())
    market_price_var_coef_plot = build_market_price_var_coef_plot(place_and_year_groups.mean())

    places_badge_count = len(selected_places)
    prices_badge_count = filtered_dataset[COLUMNS.GAS_STATION_COUNT].sum() # TODO remove overlaps
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
