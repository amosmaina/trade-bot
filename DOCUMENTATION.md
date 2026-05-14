# AI Trading Assistant - Documentation

## 1. System Overview
This is an institutional-grade AI trading analyst and execution assistant. It uses a 3-layer analysis model (Regime -> Bias -> Entry) and multiple strategies to identify high-probability setups.

## 2. Advanced Features
- **SMC Strategy (Institutional)**: Detects Liquidity Sweeps, Fair Value Gaps (FVG), and Break of Structure (BOS).
- **Multi-Strategy Engine**: Trend Following, Scalping, Breakout, and Reversal strategies.
- **Risk Management**: Automatic position sizing and 1:2 min Risk-to-Reward validation.

## 3. Installation
1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Connecting to HFM (MetaTrader 5)
1. **Download MT5**: Ensure the HFM MetaTrader 5 terminal is installed and logged in on your machine.
2. **Configure Environment**: Create a `.env` file from `.env.example`:
   ```env
   HFM_LOGIN=12345678
   HFM_PASSWORD=your_password
   HFM_SERVER=HFM-Live
   ```
3. **Enable Algo Trading**: In MT5 terminal, go to `Tools -> Options -> Expert Advisors` and check `Allow Algorithmic Trading`.

## 5. Configuration
- **Risk per Trade**: Edit `src/engine/risk_manager.py` (Default: 1%).
- **Symbols**: Edit `main.py` to change the symbols you want to scan.

## 6. Usage
To start the market scanner in simulation mode (Binance data):
```bash
python main.py
```

To start the market scanner with HFM/MT5 connection:
Modify `main.py`:
```python
assistant = TradingAssistant(use_hfm=True)
major_pairs = ['EURUSD', 'GBPUSD', 'XAUUSD'] # Use MT5 symbol names
```

## 7. Execution Flow
1. **Scan**: The bot scans markets for setups.
2. **Analyze**: Reasoning is displayed (Market Regime, HTF Bias, Strategy).
3. **Propose**: A trade proposal is outputted with SL/TP and Confidence Score.
4. **Approval**: YOU must decide to `ACCEPT` or `REJECT` the trade.
