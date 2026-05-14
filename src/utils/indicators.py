import numpy as np
import pandas as pd

class Indicators:
    @staticmethod
    def ema(series, period):
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(series, fast=12, slow=26, signal=9):
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def adx(df, period=14):
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = abs(minus_dm)
        
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift(1))
        tr3 = abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx

    @staticmethod
    def bollinger_bands(series, period=20, std_dev=2):
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def atr(df, period=14):
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift(1))
        tr3 = abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    @staticmethod
    def find_fvg(df):
        """
        Detect Fair Value Gaps (FVG)
        Bullish FVG: Low of candle 3 > High of candle 1
        Bearish FVG: High of candle 3 < Low of candle 1
        """
        fvg_list = []
        for i in range(2, len(df)):
            # Bullish FVG
            if df['low'].iloc[i] > df['high'].iloc[i-2]:
                fvg_list.append({'index': i-1, 'type': 'Bullish', 'top': df['low'].iloc[i], 'bottom': df['high'].iloc[i-2]})
            # Bearish FVG
            elif df['high'].iloc[i] < df['low'].iloc[i-2]:
                fvg_list.append({'index': i-1, 'type': 'Bearish', 'top': df['low'].iloc[i-2], 'bottom': df['high'].iloc[i]})
        return fvg_list

    @staticmethod
    def detect_liquidity_sweeps(df, lookback=20):
        """
        Detect Liquidity Sweeps
        Sweep of recent highs or lows followed by a reversal
        """
        current_high = df['high'].iloc[-1]
        current_low = df['low'].iloc[-1]
        
        recent_max = df['high'].iloc[-lookback-1:-1].max()
        recent_min = df['low'].iloc[-lookback-1:-1].min()
        
        sweep_high = current_high > recent_max and df['close'].iloc[-1] < recent_max
        sweep_low = current_low < recent_min and df['close'].iloc[-1] > recent_min
        
        return sweep_high, sweep_low

    @staticmethod
    def calculate_ofi(df, period=5):
        """
        Order Flow Imbalance (OFI)
        Calculates the net imbalance between buying and selling pressure based on price and volume.
        """
        delta_v = []
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                # Bullish imbalance: volume contributed to price increase
                delta_v.append(df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                # Bearish imbalance: volume contributed to price decrease
                delta_v.append(-df['volume'].iloc[i])
            else:
                delta_v.append(0)
        
        ofi = pd.Series(delta_v).rolling(window=period).mean()
        return ofi

    @staticmethod
    def detect_orderflow_signals(df):
        """
        Detect 4 Core Orderflow Signals:
        1. Momentum (Increasing volume with price move)
        2. Absorption (High volume but price fails to break levels)
        3. Exhaustion (Decreasing volume as price hits extremes)
        4. Imbalance (Significant OFI)
        """
        vol_sma = df['volume'].rolling(window=20).mean()
        curr_vol = df['volume'].iloc[-1]
        curr_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        
        signals = {
            'momentum': curr_vol > vol_sma.iloc[-1] * 1.5 and abs(curr_close - prev_close) > 0,
            'absorption': curr_vol > vol_sma.iloc[-1] * 2 and abs(curr_close - prev_close) < (df['high'].iloc[-1] - df['low'].iloc[-1]) * 0.2,
            'exhaustion': curr_vol < vol_sma.iloc[-1] * 0.5,
            'imbalance': abs(Indicators.calculate_ofi(df).iloc[-1]) > vol_sma.iloc[-1] * 0.5
        }
        return signals
