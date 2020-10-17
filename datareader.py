import pandas as pd
import requests
from bs4 import BeautifulSoup

"""
Get a list of options from https://m-x.ca/nego_liste_en.php
TMX website

Index and ETF options
Equity options
Currency options
Weekly options
"""
def get_list(market=str) -> pd.DataFrame:
    tmx = "https://m-x.ca/nego_liste_en.php" # TMX website, where data is taken from

    #check that parameter is of type string
    is_str1 = isinstance(market, str)
    if not is_str1:
        raise TypeError("market parameter must be of type string")

    #now get data from https://m-x.ca/nego_liste_en.php TMX website
    try:
        market = market.lower()
    except Exception as e:
        print(e)
    else:
        if market == 'index' or market == 'etf':
            market = 0
        elif market == 'equity':
            market = 1
        elif market == 'currency':
            market = 2
        elif market == 'weekly':
            market = 3
        else:
            raise Exception("Did not enter market type, choose from Index or ETF, Equity, Currency, Weekly.")
        df = pd.read_html(tmx)
        return df[market]

"""
Get options prices at predetermined dates from TMX website
Call/Puts
strike price
Bid/Ask spreads
open interest
implied volatility
volume
"""
def get(market=str,ticker_symbol=str) -> pd.DataFrame:
    tmx = "https://m-x.ca/nego_cotes_en.php" # TMX website, where data is taken from

    #check that both parameters are of type string
    is_str1 = isinstance(ticker_symbol, str)
    is_str2 = isinstance(market, str)
    if not (is_str1 and is_str2):
        raise TypeError("market & ticker_symbol parameters must be of type string")

    #now get data from https://m-x.ca/nego_liste_en.php TMX website
    try:
        market = market.lower()
        ticker_symbol = ticker_symbol.upper()
    except Exception as e:
        print(e)
    else:
        if market == ('index' or 'etf'):
            market = 0
        elif market == 'equity':
            market = 1
        elif market == 'currency':
            market = 2
        elif market == 'weekly':
            market = 3
        else:
            raise Exception("Did not enter market type, choose from Index or ETF, Equity, Currency, Weekly.")
        url = tmx + '?symbol=' + ticker_symbol + '*'
        df = pd.read_html(url)
        df[0].rename(columns={'Bid price.1':'Bid price_', 'Ask price.1':'Ask price_', 'Last Price.1':'Last Price_',
                             'Impl. vol..1':'Impl. vol_', 'Open int..1':'Open int_', 'Vol..1':'Vol_'}, inplace=True)
        return df[0].iloc[:-1] #do not include last row, rubbish information

"""
Get stock price from TMX to compare to strike price
can accept string or list of strings
"""
def get_stock(ticker_symbol=str) -> pd.DataFrame:
    tmx = "https://m-x.ca/nego_cotes_en.php" # TMX website, where data is taken from

    #check that parameter is of type string
    is_str1 = checktype(ticker_symbol) #isinstance(ticker_symbol, str)
    if not is_str1:
        raise TypeError("market parameter must be of type string")

    #download stock price, remember it is 15 minutes delayed
    try:
        symbols = []
        for n in ticker_symbol:
            symbols.append(n.upper())

    except Exception as e:
        print(e)
    else:
        price_dict = {}
        is_list = isinstance(ticker_symbol, list)
        if is_list:
            df_list = []
            for m in symbols:
                URL = tmx + '?symbol=' + m + '*'
                response = requests.get(URL)
                soup = BeautifulSoup(response.text, 'html.parser')
                x = soup.find('div', class_ = 'quote-info', attrs = 'ul')
                y = x.ul.text.split('\n')[1:-2]

                price_dict['TICKER'] = m
                for z in y:
                    key, value = z.split(':')
                    price_dict[key] = value
                tmp_df = pd.DataFrame.from_dict(price_dict, orient='index').T
                df_list.append(tmp_df)
            return pd.concat(df_list, ignore_index=True)
        else:
            ticker_symbol = ticker_symbol.upper()
            URL = tmx + '?symbol=' + ticker_symbol + '*'
            response = requests.get(URL)
            soup = BeautifulSoup(response.text, 'html.parser')
            x = soup.find('div', class_ = 'quote-info', attrs = 'ul')
            y = x.ul.text.split('\n')[1:-2]

            price_dict['TICKER'] = ticker_symbol
            for z in y:
                key, value = z.split(':')
                price_dict[key] = value
            tmp_df = pd.DataFrame.from_dict(price_dict, orient='index').T
            return tmp_df

def checktype(obj):
    return bool(obj) and all(isinstance(elem, str) for elem in obj)
