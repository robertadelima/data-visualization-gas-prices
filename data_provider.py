import pandas as pd

gas_dataset_path = "data/dados-ANP-2013-2020.csv"
cities_dataset_path = "data/dados-IBGE-municipios.csv"

# Import data
__gas_data = pd.read_csv(gas_dataset_path, sep=';', encoding='cp1252')
__cities_data = pd.read_csv(cities_dataset_path, sep=';', encoding='cp1252')

def __normalize_city_names(series):
    '''Remove accents and upper case'''
    return series.str.normalize('NFKD')\
                 .str.encode('ascii', errors='ignore')\
                 .str.decode('utf-8')\
                 .str.upper()


def __merge_city_data(gas_data, cities_data):
    city_names = cities_data['NOME MUNICIPIO']
    cities_data['NOME MUNICIPIO'] = __normalize_city_names(city_names)

    return pd.merge(gas_data,            cities_data,
                    left_on='MUNICÍPIO', right_on='NOME MUNICIPIO',
                    how='left')

DATASET = __merge_city_data(__gas_data, __cities_data)

class COLUMNS:
    MONTH = 'MÊS'
    PRODUCT = 'PRODUTO'
    CITY = 'MUNICÍPIO'
    REGION = 'REGIÃO'
    STATE = 'ESTADO'
    CITY = 'MUNICÍPIO'
    GAS_STATION_COUNT = 'NÚMERO DE POSTOS PESQUISADOS'
    UNIT = 'UNIDADE DE MEDIDA'

    MARKET_PRICE_MEAN = 'PREÇO MÉDIO REVENDA'
    MARKET_PRICE_STD = 'DESVIO PADRÃO REVENDA'
    MARKET_PRICE_MIN = 'PREÇO MÍNIMO REVENDA'
    MARKET_PRICE_MAX = 'PREÇO MÁXIMO REVENDA'
    MARKET_PRICE_VAR_COEF = 'COEF DE VARIAÇÃO REVENDA'

    MARKET_MARGIN = 'MARGEM MÉDIA REVENDA'

    DIST_PRICE_MEAN = 'PREÇO MÉDIO DISTRIBUIÇÃO'
    DIST_PRICE_STD = 'DESVIO PADRÃO DISTRIBUIÇÃO'
    DIST_PRICE_MIN = 'PREÇO MÍNIMO DISTRIBUIÇÃO'
    DIST_PRICE_MAX = 'PREÇO MÁXIMO DISTRIBUIÇÃO'
    DIST_PRICE_VAR_COEF = 'COEF DE VARIAÇÃO DISTRIBUIÇÃO'

    LATITUDE = 'LATITUDE'
    LONGITUDE = 'LONGITUDE'
