import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Import data
gas_prices = pd.read_csv("dados-ANP-2013-2020.csv", sep=';', encoding='cp1252')


# App layout
app.layout = html.Div([

    html.H1("Preços dos Combustíveis - Santa Catarina, Brasil", style={'text-align': 'center'}),

])


# Run
if __name__ == '__main__':
    app.run_server(debug=True)