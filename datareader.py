import pandas as pd
import requests
from bs4 import BeautifulSoup

"""
Get a list of options from https://www.m-x.ca/en/trading/data/options-list
TMX website

ETF options
Index options
Equity options
Currency options
Weekly options
"""
def get_list(market=str) -> pd.DataFrame:
    tmx = 'https://www.m-x.ca/en/trading/data/options-list' # TMX website, where data is taken from

    # check that parameter is of type string
    is_str1 = isinstance(market, str)
    if not is_str1:
        raise TypeError('market parameter must be of type string')

    # now get data from https://www.m-x.ca/en/trading/data/options-list TMX website
    try:
        market = '#'+ market.lower()
        df = pd.read_html(tmx+market)
    except Exception as e:
        print(e)
    else:
        match market:
            case '#etf':
                return df[0]
            case '#index':
                return df[1]
            case '#equity':
                return df[2]
            case '#currency':
                return df[3]
            case '#weekly':
                return df[4]
            case _:
                return df

"""
Get options prices at predetermined dates from TMX website
Call/Puts
strike price
Bid/Ask spreads
open interest
implied volatility
volume
"""
def get_price(ticker_symbol=str) -> list[pd.DataFrame]:
    tmx = 'https://www.m-x.ca/en/trading/data/quotes' # TMX website, where data is taken from

    # check that both parameters are of type string
    is_str1 = isinstance(ticker_symbol, str)
    if not is_str1:
        raise TypeError('ticker_symbol parameters must be of type string')

    # now get data from https://www.m-x.ca/en/trading/data/quotes TMX website
    try:
        price_dict = {}
        ticker_symbol = ticker_symbol.upper()
        url = tmx + '?symbol=' + ticker_symbol + '*#quotes'
        df = pd.read_html(url)[0].iloc[:-1] # do not include last row, rubbish information

        # get metadata from the table at the top of page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        last_update = soup.find('div', class_ = 'quote-info').find('p')
        k, v = last_update.text.split(': ')
        price_dict[k] = v
        
        x = soup.find('div', class_ = 'quote-info', attrs = 'ul')
        y = x.ul.text.split('\n')[1:-1]

        price_dict['TICKER'] = ticker_symbol
        for z in y:
            key, value = z.split(':')
            price_dict[key] = value
        meta_df = pd.DataFrame.from_dict(price_dict, orient='index').T
    except Exception as e:
        print(e)
    else:
        return meta_df, df
