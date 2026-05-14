import MetaTrader5 as mt5
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class HFMConnector:
    def __init__(self):
        self.login = int(os.getenv("HFM_LOGIN", 0))
        self.password = os.getenv("HFM_PASSWORD", "")
        self.server = os.getenv("HFM_SERVER", "")
        self.initialized = False

    def connect(self):
        if not mt5.initialize():
            print("mt5.initialize() failed, error code =", mt5.last_error())
            return False
        
        authorized = mt5.login(self.login, password=self.password, server=self.server)
        if authorized:
            print(f"Connected to HFM Account: {self.login}")
            self.initialized = True
            return True
        else:
            print(f"Failed to connect to HFM, error code = {mt5.last_error()}")
            return False

    def get_ohlcv(self, symbol, timeframe, count=100):
        """
        Fetch OHLCV from MT5
        Timeframe examples: mt5.TIMEFRAME_H1, mt5.TIMEFRAME_D1
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.rename(columns={'time': 'timestamp', 'tick_volume': 'volume'}, inplace=True)
        return df

    def execute_trade(self, symbol, signal, volume, stop_loss, take_profit):
        """
        Execute trade on MT5
        """
        if not self.initialized:
            if not self.connect(): return False

        order_type = mt5.ORDER_TYPE_BUY if signal == 'LONG' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).ask if signal == 'LONG' else mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "sl": float(stop_loss),
            "tp": float(take_profit),
            "magic": 123456,
            "comment": "AI Trading Assistant",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed, retcode={result.retcode}")
            return False
            
        print(f"Trade executed: {signal} {volume} {symbol} at {price}")
        return True

    def shutdown(self):
        mt5.shutdown()
