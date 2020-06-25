import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

gas_prices = pd.read_csv("dados-ANP-2013-2020.csv", sep=';', encoding='cp1252')
print(gas_prices.head())

