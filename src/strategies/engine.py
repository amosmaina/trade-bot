from src.utils.indicators import Indicators

class BaseStrategy:
    def __init__(self, name):
        self.name = name

    def check_conditions(self, df):
        raise NotImplementedError

class TrendFollowing(BaseStrategy):
    def __init__(self):
        super().__init__("Trend Following")

    def check_conditions(self, df):
        ema20 = Indicators.ema(df['close'], 20)
        ema50 = Indicators.ema(df['close'], 50)
        ema200 = Indicators.ema(df['close'], 200)
        rsi = Indicators.rsi(df['close'], 14)
        _, _, hist = Indicators.macd(df['close'])
        
        curr_idx = -1
        
        long_cond = (
            ema20.iloc[curr_idx] > ema50.iloc[curr_idx] > ema200.iloc[curr_idx] and
            50 < rsi.iloc[curr_idx] < 70 and
            hist.iloc[curr_idx] > 0
        )
        
        short_cond = (
            ema20.iloc[curr_idx] < ema50.iloc[curr_idx] < ema200.iloc[curr_idx] and
            30 < rsi.iloc[curr_idx] < 50 and
            hist.iloc[curr_idx] < 0
        )
        
        if long_cond: return 'LONG'
        if short_cond: return 'SHORT'
        return 'NO_TRADE'

class Scalping(BaseStrategy):
    def __init__(self):
        super().__init__("Scalping")

    def check_conditions(self, df):
        rsi = Indicators.rsi(df['close'], 14)
        upper, sma, lower = Indicators.bollinger_bands(df['close'], 20, 2)
        
        curr_idx = -1
        
        # Long: RSI < 30 (oversold) and price rejects lower band
        long_cond = (
            rsi.iloc[curr_idx] < 35 and 
            df['low'].iloc[curr_idx] <= lower.iloc[curr_idx] and
            df['close'].iloc[curr_idx] > lower.iloc[curr_idx]
        )
        
        # Short: RSI > 70 (overbought) and price rejects upper band
        short_cond = (
            rsi.iloc[curr_idx] > 65 and 
            df['high'].iloc[curr_idx] >= upper.iloc[curr_idx] and
            df['close'].iloc[curr_idx] < upper.iloc[curr_idx]
        )
        
        if long_cond: return 'LONG'
        if short_cond: return 'SHORT'
        return 'NO_TRADE'

class BreakoutStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Breakout")

    def check_conditions(self, df):
        recent_high = df['high'].rolling(window=20).max().shift(1)
        recent_low = df['low'].rolling(window=20).min().shift(1)
        
        curr_idx = -1
        
        long_cond = (
            df['close'].iloc[curr_idx] > recent_high.iloc[curr_idx] and
            df['volume'].iloc[curr_idx] > df['volume'].rolling(window=20).mean().iloc[curr_idx] * 1.5
        )
        
        short_cond = (
            df['close'].iloc[curr_idx] < recent_low.iloc[curr_idx] and
            df['volume'].iloc[curr_idx] > df['volume'].rolling(window=20).mean().iloc[curr_idx] * 1.5
        )
        
        if long_cond: return 'LONG'
        if short_cond: return 'SHORT'
        return 'NO_TRADE'

class ReversalStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Reversal")

    def check_conditions(self, df):
        rsi = Indicators.rsi(df['close'], 14)
        
        curr_idx = -1
        prev_idx = -2
        
        # Bullish Divergence (Simplified)
        long_cond = (
            df['close'].iloc[curr_idx] < df['close'].iloc[prev_idx] and
            rsi.iloc[curr_idx] > rsi.iloc[prev_idx] and
            rsi.iloc[curr_idx] < 30
        )
        
        # Bearish Divergence (Simplified)
        short_cond = (
            df['close'].iloc[curr_idx] > df['close'].iloc[prev_idx] and
            rsi.iloc[curr_idx] < rsi.iloc[prev_idx] and
            rsi.iloc[curr_idx] > 70
        )
        
        if long_cond: return 'LONG'
        if short_cond: return 'SHORT'
        return 'NO_TRADE'

class SMCStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Smart Money Concepts")

    def check_conditions(self, df):
        """
        SMC Advanced: Liquidity Sweeps + FVG + BOS + Order Flow Imbalance (OFI)
        Includes 4 Orderflow Signals: Momentum, Absorption, Exhaustion, Imbalance
        """
        # 1. Detect Liquidity Sweeps
        sweep_high, sweep_low = Indicators.detect_liquidity_sweeps(df)
        
        # 2. Find recent FVG (Imbalance)
        fvgs = Indicators.find_fvg(df.tail(15))
        has_bullish_fvg = any(f['type'] == 'Bullish' for f in fvgs)
        has_bearish_fvg = any(f['type'] == 'Bearish' for f in fvgs)
        
        # 3. Order Flow Signals
        of_signals = Indicators.detect_orderflow_signals(df)
        ofi = Indicators.calculate_ofi(df).iloc[-1]
        
        # 4. BOS (Break of Structure)
        recent_high = df['high'].iloc[-20:-1].max()
        recent_low = df['low'].iloc[-20:-1].min()
        current_close = df['close'].iloc[-1]
        
        # Long: Sweep low + Bullish FVG/OFI + (Absorption or Momentum)
        if (sweep_low or current_close > recent_high) and (has_bullish_fvg or ofi > 0):
            if of_signals['momentum'] or of_signals['absorption'] or of_signals['imbalance']:
                return 'LONG'
            
        # Short: Sweep high + Bearish FVG/OFI + (Absorption or Momentum)
        if (sweep_high or current_close < recent_low) and (has_bearish_fvg or ofi < 0):
            if of_signals['momentum'] or of_signals['absorption'] or of_signals['imbalance']:
                return 'SHORT'
            
        return 'NO_TRADE'
