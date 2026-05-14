import ccxt
import pandas as pd
import time
from datetime import datetime

class DataLoader:
    def __init__(self, exchange_id='binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
        })

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetch OHLCV data from exchange
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_available_symbols(self):
        """
        Get all active symbols from exchange
        """
        try:
            markets = self.exchange.load_markets()
            return [symbol for symbol, market in markets.items() if market['active']]
        except Exception as e:
            print(f"Error loading markets: {e}")
            return []
