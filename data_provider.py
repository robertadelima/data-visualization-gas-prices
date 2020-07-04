import pandas as pd
import locale as lcl

gas_dataset_path = "data/dados-ANP-2013-2020.csv"
cities_dataset_path = "data/dados-IBGE-municipios.csv"

# Import data
__gas_data = pd.read_csv(gas_dataset_path,
                         sep=';', encoding='cp1252',
                         decimal=',', na_values=['-'])
__cities_data = pd.read_csv(cities_dataset_path,
                            sep=';', encoding='cp1252')

# Define aliases for quickly accessing columns
class COLUMNS:
    MONTH = 'MÊS'
    PRODUCT = 'PRODUTO'
    CITY = 'MUNICÍPIO'
    REGION = 'REGIÃO'
    STATE = 'ESTADO'
    UF = 'UF'
    CITY_NAME = 'NOME MUNICIPIO'
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

def __parse_dates(series):
    default_locale_str = lcl.getlocale()[0]
    lcl.setlocale(lcl.LC_ALL, 'pt_BR')
    parsed_series = pd.to_datetime(series, format='%b/%y')
    lcl.setlocale(lcl.LC_ALL, default_locale_str)
    return parsed_series

def __normalize_city_names(series):
    '''Remove accents and upper case'''
    return series.str.normalize('NFKD')\
                 .str.encode('ascii', errors='ignore')\
                 .str.decode('utf-8')\
                 .str.upper()

def __merge_city_data(gas_data, cities_data):
    city_names = cities_data['NOME MUNICIPIO']
    cities_data['NOME MUNICIPIO'] = __normalize_city_names(city_names)

    # Remove duplicated city names
    unique_cities_data = cities_data.drop_duplicates(subset=[COLUMNS.CITY_NAME])

    return pd.merge(gas_data,            unique_cities_data,
                    left_on='MUNICÍPIO', right_on='NOME MUNICIPIO',
                    how='inner')


__gas_data[COLUMNS.MONTH] = __parse_dates(__gas_data[COLUMNS.MONTH])
__df = __merge_city_data(__gas_data, __cities_data)

DATASET = __df
PRODUCTS = list(__df[COLUMNS.PRODUCT].unique())
YEARS = list(__df[COLUMNS.MONTH].dt.year.unique())

REGIONS = list(__df[COLUMNS.REGION].unique())
STATES = list(__df[COLUMNS.STATE].unique())
CITIES_UF = list((__df[COLUMNS.CITY] + ' (' + __df[COLUMNS.UF] + ')').dropna().unique())

def remove_uf(city_name):
    return ' '.join(city_name.split()[:-1])

def remove_region_prefix(city_name):
    return ' '.join(city_name.split()[1:])

def __generate_places_dict():

    regions = { f'region_{name}': f'REGIAO {name}' for name in REGIONS }
    states = { f'state_{name}': name for name in STATES }
    cities = { f'city_{remove_uf(name_uf)}': name_uf for name_uf in CITIES_UF }

    return { **regions, **states, **cities }

PLACES_DICT = __generate_places_dict()

def generate_aggregate_data(dataset):
    COLUMNS.PLACE_TYPE = 'TIPO DO LOCAL'
    COLUMNS.PLACE_NAME = 'NOME DO LOCAL'

    dataset[COLUMNS.PLACE_TYPE] = 'CIDADE'
    dataset[COLUMNS.PLACE_NAME] = dataset[COLUMNS.CITY]\
                                  .apply(lambda name: PLACES_DICT['city_' + name])

    column_aggregations = { COLUMNS.GAS_STATION_COUNT: 'sum',
                            COLUMNS.MARKET_PRICE_MEAN: 'mean',
                            COLUMNS.MARKET_PRICE_STD: 'mean', # ?
                            COLUMNS.MARKET_PRICE_MIN: 'min',
                            COLUMNS.MARKET_PRICE_MAX: 'max',
                            COLUMNS.MARKET_PRICE_VAR_COEF: 'mean', # ?
                            COLUMNS.MARKET_MARGIN: 'mean',
                            COLUMNS.DIST_PRICE_MEAN: 'mean',
                            COLUMNS.DIST_PRICE_STD: 'mean', # ?
                            COLUMNS.DIST_PRICE_MIN: 'min',
                            COLUMNS.DIST_PRICE_MAX: 'max',
                            COLUMNS.DIST_PRICE_VAR_COEF: 'mean', # ?
                            COLUMNS.LATITUDE: 'mean', # ?
                            COLUMNS.LONGITUDE: 'mean', # ?
                            }

    def group_and_aggregate(columns):
        return dataset.groupby(columns)\
                      .agg(column_aggregations)\
                      .reset_index()

    states_data = group_and_aggregate([COLUMNS.STATE,
                                       COLUMNS.MONTH])
    states_data[COLUMNS.PLACE_TYPE] = 'ESTADO'
    states_data[COLUMNS.PLACE_NAME] = states_data[COLUMNS.STATE]\
                                    .apply(lambda name: PLACES_DICT['state_' + name])

    regions_data = group_and_aggregate([COLUMNS.REGION,
                                       COLUMNS.MONTH])
    regions_data[COLUMNS.PLACE_TYPE] = 'REGIAO'
    regions_data[COLUMNS.PLACE_NAME] = regions_data[COLUMNS.REGION]\
                                    .apply(lambda name: PLACES_DICT['region_' + name])

    return dataset.append(states_data)\
                  .append(regions_data)

