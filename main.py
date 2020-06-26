import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def clean_data_and_generate_dataset():
    # Import data
    df1 = pd.read_csv("dados-ANP-2013-2020.csv", sep=';', encoding='cp1252')
    df2 = pd.read_csv("dados-IBGE-municipios.csv", sep=';', encoding='cp1252')
    # Removing accents
    df2['NOME MUNICIPIO'] = df2['NOME MUNICIPIO'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    # IBGE data to upper case
    df2['NOME MUNICIPIO'] = df2['NOME MUNICIPIO'].str.upper()
    # Left join
    df3 = pd.merge(df1, df2, left_on='MUNICÍPIO', right_on='NOME MUNICIPIO', how ='left') 
    return df3

df = clean_data_and_generate_dataset()
print(df.head(3))

app = dash.Dash(__name__)

city_map = html.Div([])

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
    city_map,
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

# Run
if __name__ == '__main__':
    app.run_server(debug=True)
