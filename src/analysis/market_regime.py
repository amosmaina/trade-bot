import pandas_ta as ta
import pandas as pd

class MarketRegime:
    @staticmethod
    def analyze(df_1h, df_4h, df_1d):
        """
        Analyze Market Regime and Higher Timeframe Bias
        LAYER 1 & LAYER 2
        """
        results = {
            'regime': 'Unknown',
            'bias': 'Neutral',
            'strength': 0,
            'details': {}
        }

        # Analyze 1D for Macro Trend (Layer 2)
        ema200_1d = ta.ema(df_1d['close'], length=200)
        ema50_1d = ta.ema(df_1d['close'], length=50)
        
        current_price_1d = df_1d['close'].iloc[-1]
        
        if current_price_1d > ema200_1d.iloc[-1] and ema50_1d.iloc[-1] > ema200_1d.iloc[-1]:
            results['bias'] = 'Bullish'
        elif current_price_1d < ema200_1d.iloc[-1] and ema50_1d.iloc[-1] < ema200_1d.iloc[-1]:
            results['bias'] = 'Bearish'
        else:
            results['bias'] = 'Ranging'

        # Analyze 1H for Market Regime (Layer 1)
        adx = ta.adx(df_1h['high'], df_1h['low'], df_1h['close'])
        current_adx = adx['ADX_14'].iloc[-1]
        
        if current_adx > 25:
            results['regime'] = 'Trending' if results['bias'] != 'Ranging' else 'Volatile'
        elif current_adx < 20:
            results['regime'] = 'Ranging'
        else:
            results['regime'] = 'Accumulating/Distributing'

        # Institutional Concepts (Layer 2)
        # Check for Premium/Discount zones (Fib 0.5 of 1D range)
        low_1d = df_1d['low'].tail(20).min()
        high_1d = df_1d['high'].tail(20).max()
        mid_point = (high_1d + low_1d) / 2
        
        results['details']['zone'] = 'Premium' if current_price_1d > mid_point else 'Discount'
        results['strength'] = current_adx
        
        return results
