import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Import data
df1 = pd.read_csv("dados-ANP-2013-2020.csv", sep=';', encoding='cp1252')
df2 = pd.read_csv("dados-IBGE-municipios.csv", sep=';', encoding='cp1252')
# Removing accents
df2['NOME MUNICIPIO'] = df2['NOME MUNICIPIO'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
# IBGE data to upper case
df2['NOME MUNICIPIO'] = df2['NOME MUNICIPIO'].str.upper()
# Left join
df3 = pd.merge(df1, df2, left_on='MUNICÍPIO', right_on='NOME MUNICIPIO', how ='left') 
print(df3.head())


# App layout
app.layout = html.Div([

    html.H1("Preços dos Combustíveis - Santa Catarina, Brasil", style={'text-align': 'center'}),

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
    
    dff = df2.copy()
    dff = dff[dff["UF"].isin(opcao_selecionada)]

    px.set_mapbox_access_token(open(".mapbox_token.txt").read())
    fig = px.scatter_mapbox(dff, lat="LATITUDE", lon="LONGITUDE", color_continuous_scale=px.colors.cyclical.IceFire, 
        size_max=30, zoom=5)
    return container, fig

# Run
if __name__ == '__main__':
    app.run_server(debug=True)