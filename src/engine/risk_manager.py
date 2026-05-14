class RiskManager:
    def __init__(self, risk_per_trade=0.01, max_drawdown=0.05):
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = max_drawdown

    def calculate_position_size(self, balance, entry_price, stop_loss):
        """
        Calculate position size based on risk
        """
        risk_amount = balance * self.risk_per_trade
        stop_loss_pct = abs(entry_price - stop_loss) / entry_price
        
        if stop_loss_pct == 0:
            return 0
            
        position_size = risk_amount / stop_loss_pct
        return position_size

    def validate_trade(self, entry, stop_loss, take_profit):
        """
        Validate Risk-to-Reward Ratio (min 1:2)
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0: return False
        
        rr_ratio = reward / risk
        return rr_ratio >= 2.0

    def get_probability_score(self, strategy_results, market_regime):
        """
        Mathematical probability-weighted outcome
        """
        score = 0
        # Strategy confidence
        if strategy_results != 'NO_TRADE':
            score += 40
            
        # Alignment with Higher Timeframe Bias
        if market_regime['bias'] != 'Neutral':
            score += 30
            
        # Market Regime alignment
        if market_regime['regime'] == 'Trending':
            score += 30
            
        return score
