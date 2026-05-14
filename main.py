import os
from dotenv import load_dotenv
from src.utils.data_loader import DataLoader
from src.analysis.market_regime import MarketRegime
from src.strategies.engine import TrendFollowing, SMCStrategy
from src.engine.risk_manager import RiskManager

load_dotenv()

class TradingAssistant:
    def __init__(self):
        self.data_loader = DataLoader()
        self.risk_manager = RiskManager()
        self.strategies = [TrendFollowing(), SMCStrategy()]
        self.market_regime = MarketRegime()

    def analyze_market(self, symbol):
        print(f"\n--- ANALYZING {symbol} ---")
        
        # Layer 1 & 2: Market Context
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
        for strategy in self.strategies:
            signal = strategy.check_conditions(df_1h)
            if signal != 'NO_TRADE':
                self.propose_trade(symbol, signal, strategy, regime_data, df_1h)
                return

        print("No high-probability setups found.")

    def propose_trade(self, symbol, signal, strategy, regime_data, df_1h):
        entry = df_1h['close'].iloc[-1]
        
        # Simple SL/TP for proposal (should be more dynamic in production)
        atr = 100 # Placeholder for ATR calculation
        if signal == 'LONG':
            stop_loss = entry - (atr * 2)
            take_profit = entry + (atr * 5)
        else:
            stop_loss = entry + (atr * 2)
            take_profit = entry - (atr * 5)

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
    # Default to BTC/USDT for initial scan
    assistant.analyze_market('BTC/USDT')
