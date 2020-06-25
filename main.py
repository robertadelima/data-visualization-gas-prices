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

])


# Run
if __name__ == '__main__':
    app.run_server(debug=True)