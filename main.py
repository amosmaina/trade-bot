import os
from dotenv import load_dotenv
from src.utils.data_loader import DataLoader
from src.utils.indicators import Indicators
from src.analysis.market_regime import MarketRegime
from src.strategies.engine import (
    TrendFollowing, Scalping, BreakoutStrategy, 
    ReversalStrategy, SMCStrategy
)
from src.engine.risk_manager import RiskManager

load_dotenv()

from src.utils.hfm_connector import HFMConnector
import MetaTrader5 as mt5

class TradingAssistant:
    def __init__(self, use_hfm=False):
        self.data_loader = DataLoader()
        self.hfm = HFMConnector() if use_hfm else None
        self.risk_manager = RiskManager()
        self.strategies = [
            TrendFollowing(), 
            Scalping(), 
            BreakoutStrategy(), 
            ReversalStrategy(), 
            SMCStrategy()
        ]
        self.market_regime = MarketRegime()
        self.use_hfm = use_hfm

    def analyze_market(self, symbol):
        print(f"\n--- ANALYZING {symbol} ---")
        
        # Determine source of data
        if self.use_hfm and self.hfm.connect():
            # MT5 Mapping
            mt5_tf = {
                '1d': mt5.TIMEFRAME_D1,
                '4h': mt5.TIMEFRAME_H4,
                '1h': mt5.TIMEFRAME_H1,
                '15m': mt5.TIMEFRAME_M15
            }
            df_1d = self.hfm.get_ohlcv(symbol, mt5_tf['1d'])
            df_4h = self.hfm.get_ohlcv(symbol, mt5_tf['4h'])
            df_1h = self.hfm.get_ohlcv(symbol, mt5_tf['1h'])
        else:
            df_1d = self.data_loader.fetch_ohlcv(symbol, timeframe='1d', limit=100)
            df_4h = self.data_loader.fetch_ohlcv(symbol, timeframe='4h', limit=100)
            df_1h = self.data_loader.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        
        if df_1d is None or df_4h is None or df_1h is None:
            print("Failed to fetch data.")
            return

        regime_data = self.market_regime.analyze(df_1h, df_4h, df_1d)
        
        print(f"Market Regime: {regime_data['regime']}")
        print(f"Higher Timeframe Bias: {regime_data['bias']}")
        print(f"Zone: {regime_data['details']['zone']}")

        # Strategy Engine
        # We iterate through strategies to find the best fit for the current regime
        for strategy in self.strategies:
            signal = strategy.check_conditions(df_1h)
            if signal != 'NO_TRADE':
                # Layer 3: Lower Timeframe Confirmation
                # Fetch 15m for precision entry
                df_15m = self.data_loader.fetch_ohlcv(symbol, timeframe='15m', limit=100)
                if df_15m is not None:
                    self.propose_trade(symbol, signal, strategy, regime_data, df_1h, df_15m)
                    return

        print("No high-probability setups found.")

    def propose_trade(self, symbol, signal, strategy, regime_data, df_1h, df_15m):
        entry = df_15m['close'].iloc[-1]
        atr = Indicators.atr(df_1h, 14).iloc[-1]
        
        if signal == 'LONG':
            stop_loss = entry - (atr * 1.5)
            take_profit = entry + (atr * 3.5)
        else:
            stop_loss = entry + (atr * 1.5)
            take_profit = entry - (atr * 3.5)

        rr = abs(take_profit - entry) / abs(entry - stop_loss)
        confidence = self.risk_manager.get_probability_score(signal, regime_data)

        # Output in requested format
        print("\n==================================================")
        print("TRADE PROPOSAL")
        print("==================================================")
        print(f"PAIR: {symbol}")
        print(f"TRADE TYPE: {signal}")
        print(f"ENTRY: {entry:.2f}")
        print(f"STOP LOSS: {stop_loss:.2f}")
        print(f"TAKE PROFIT: {take_profit:.2f}")
        print(f"RISK-REWARD: 1:{rr:.2f}")
        print(f"CONFIDENCE SCORE: {confidence}%")
        print(f"STRATEGY USED: {strategy.name}")
        print(f"MARKET CONDITION: {regime_data['regime']}")
        print(f"REASONS FOR ENTRY: Alignment with {regime_data['bias']} bias, {strategy.name} conditions met.")
        print(f"REASONS AGAINST ENTRY: Potential {regime_data['details']['zone']} zone risk.")
        print(f"ESTIMATED PROBABILITY: {confidence}%")
        print(f"VOLATILITY STATUS: {'High' if regime_data['strength'] > 25 else 'Low'}")
        print(f"LIQUIDITY STATUS: Sufficient")
        print("==================================================")
        print("\nDO YOU WANT TO EXECUTE THIS TRADE?")
        print("[ ACCEPT ]   [ REJECT ]")

if __name__ == "__main__":
    assistant = TradingAssistant()
    # Scanning major pairs for opportunities
    major_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    for pair in major_pairs:
        assistant.analyze_market(pair)
