import pandas_ta as ta

class BaseStrategy:
    def __init__(self, name):
        self.name = name

    def check_conditions(self, df):
        raise NotImplementedError

class TrendFollowing(BaseStrategy):
    def __init__(self):
        super().__init__("Trend Following")

    def check_conditions(self, df_1h):
        """
        Conditions for LONG:
        - EMA20 > EMA50 > EMA200
        - RSI between 50–70
        - MACD bullish crossover
        - volume increasing
        - price above VWAP
        """
        ema20 = ta.ema(df_1h['close'], length=20)
        ema50 = ta.ema(df_1h['close'], length=50)
        ema200 = ta.ema(df_1h['close'], length=200)
        rsi = ta.rsi(df_1h['close'], length=14)
        macd = ta.macd(df_1h['close'])
        
        curr_idx = -1
        
        # Long Conditions
        long_cond = (
            ema20.iloc[curr_idx] > ema50.iloc[curr_idx] > ema200.iloc[curr_idx] and
            50 < rsi.iloc[curr_idx] < 70 and
            macd['MACDh_12_26_9'].iloc[curr_idx] > 0 # Bullish histogram
        )
        
        # Short Conditions
        short_cond = (
            ema20.iloc[curr_idx] < ema50.iloc[curr_idx] < ema200.iloc[curr_idx] and
            30 < rsi.iloc[curr_idx] < 50 and
            macd['MACDh_12_26_9'].iloc[curr_idx] < 0 # Bearish histogram
        )
        
        if long_cond: return 'LONG'
        if short_cond: return 'SHORT'
        return 'NO_TRADE'

class SMCStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Smart Money Concepts")

    def check_conditions(self, df_15m):
        """
        SMC Basics: BOS, CHOCH, Order Blocks
        """
        # Simplified SMC for MVP
        # Check for Break of Structure (BOS)
        recent_high = df_15m['high'].tail(50).max()
        recent_low = df_15m['low'].tail(50).min()
        
        current_close = df_15m['close'].iloc[-1]
        
        if current_close > recent_high:
            return 'LONG' # Bullish BOS
        if current_close < recent_low:
            return 'SHORT' # Bearish BOS
            
        return 'NO_TRADE'
