from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
import os
from src.utils.data_loader import DataLoader
from src.analysis.market_regime import MarketRegime
from src.strategies.engine import TrendFollowing, Scalping, BreakoutStrategy, ReversalStrategy, SMCStrategy
from src.engine.risk_manager import RiskManager
from src.analysis.news_analyzer import NewsAnalyzer
from src.utils.ai_insights import AIInsightGenerator

app = Flask(__name__, static_folder='.')
CORS(app)

class TradingSystemState:
    def __init__(self):
        self.trades = []
        self.analysis_results = {}
        self.is_running = False
        self.mode = "DEMO" # DEMO or LIVE
        self.symbols = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'USD/CHF', 'NZD/USD',
            'XAU/USD', 'XAG/USD', # Gold & Silver
            'BTC/USDT', 'ETH/USDT'
        ]
        self.data_loader = DataLoader()
        self.market_regime = MarketRegime()
        self.news_analyzer = NewsAnalyzer()
        self.risk_manager = RiskManager()
        self.ai_engine = AIInsightGenerator()
        self.strategies = [
            TrendFollowing(), Scalping(), BreakoutStrategy(), ReversalStrategy(), SMCStrategy()
        ]

    def update_analysis(self):
        while self.is_running:
            for symbol in self.symbols:
                try:
                    # Simulation: HTF Analysis
                    df_1d = self.data_loader.fetch_ohlcv(symbol, '1d', 100)
                    df_4h = self.data_loader.fetch_ohlcv(symbol, '4h', 100)
                    df_1h = self.data_loader.fetch_ohlcv(symbol, '1h', 100)
                    
                    if df_1d is not None and df_1h is not None:
                        regime = self.market_regime.analyze(df_1h, df_4h, df_1d)
                        sentiment = self.news_analyzer.get_market_sentiment(symbol)
                        
                        # Generate AI Insights every few cycles or for active setups
                        ai_insight = self.ai_engine.generate_market_insight(symbol, regime, sentiment)
                        
                        self.analysis_results[symbol] = {
                            "regime": regime['regime'],
                            "bias": regime['bias'],
                            "zone": regime['details'].get('zone', 'N/A'),
                            "sentiment": sentiment['status'],
                            "sentiment_reason": sentiment['reason'],
                            "ai_insight": ai_insight,
                            "price": df_1h['close'].iloc[-1],
                            "timestamp": time.time()
                        }
                        
                        # Check strategies
                        for strategy in self.strategies:
                            signal = strategy.check_conditions(df_1h)
                            if signal != 'NO_TRADE':
                                # Propose trade logic (stored in state for frontend)
                                self.propose_simulated_trade(symbol, signal, strategy, regime)
                                
                except Exception as e:
                    print(f"Error analyzing {symbol}: {e}")
            time.sleep(30) # Wait 30s between scans

    def propose_simulated_trade(self, symbol, signal, strategy, regime):
        # Prevent duplicate proposals for same symbol/strategy
        trade_id = f"{symbol}_{strategy.name}_{signal}"
        if any(t['id'] == trade_id for t in self.trades):
            return

        proposal = {
            "id": trade_id,
            "symbol": symbol,
            "type": signal,
            "strategy": strategy.name,
            "confidence": self.risk_manager.get_probability_score(signal, regime),
            "status": "PENDING",
            "timestamp": time.time()
        }
        self.trades.insert(0, proposal)
        if len(self.trades) > 50: self.trades.pop()

state = TradingSystemState()

@app.route('/test')
def test():
    return "Server is working"

@app.route('/')
def serve_index():
    print("Serving index.html")
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        print(f"Error serving index: {e}")
        return str(e), 500

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify({
        "mode": state.mode,
        "is_running": state.is_running,
        "symbols": state.symbols,
        "analysis": state.analysis_results,
        "trades": state.trades
    })

@app.route('/api/toggle', methods=['POST'])
def toggle_system():
    data = request.json
    state.mode = data.get("mode", "DEMO")
    
    if not state.is_running:
        state.is_running = True
        threading.Thread(target=state.update_analysis, daemon=True).start()
    else:
        state.is_running = False
        
    return jsonify({"status": "success", "is_running": state.is_running})

@app.route('/api/trade/action', methods=['POST'])
def trade_action():
    data = request.json
    trade_id = data.get("id")
    action = data.get("action") # ACCEPT or REJECT
    
    for trade in state.trades:
        if trade['id'] == trade_id:
            trade['status'] = "EXECUTED" if action == "ACCEPT" else "REJECTED"
            break
            
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
