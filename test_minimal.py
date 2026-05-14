import ccxt
import pandas as pd
# import pandas_ta as ta # Commenting this out to test

print("Starting analysis...")
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=5)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
print(df.head())
