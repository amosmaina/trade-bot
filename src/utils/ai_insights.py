import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIInsightGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def generate_market_insight(self, symbol, regime_data, news_sentiment):
        """
        Generate deep AI analysis using OpenAI GPT-4o
        """
        if not self.client:
            return "AI Analysis unavailable: Please configure OPENAI_API_KEY in .env"

        prompt = f"""
        You are an elite institutional-grade quantitative trading analyst.
        Provide a concise, professional analysis for the following market data:
        
        Asset: {symbol}
        Market Regime: {regime_data['regime']}
        Higher Timeframe Bias: {regime_data['bias']}
        Trading Zone: {regime_data['details'].get('zone', 'N/A')}
        News Sentiment: {news_sentiment['status']}
        Sentiment Reason: {news_sentiment['reason']}
        
        Focus on:
        1. Mathematical probability of current trend continuation vs reversal.
        2. Institutional liquidity considerations.
        3. Risk warning based on news events.
        
        Keep the response under 100 words. Use professional institutional terminology.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional hedge fund quant analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI Analysis Error: {str(e)}"

    def analyze_trade_setup(self, trade_proposal):
        """
        Deep dive into a specific trade setup
        """
        if not self.client:
            return "Setup validation unavailable."

        prompt = f"""
        Analyze this trade setup for {trade_proposal['symbol']}:
        Type: {trade_proposal['type']}
        Strategy: {trade_proposal['strategy']}
        Confidence: {trade_proposal['confidence']}%
        
        Verify if this aligns with institutional order flow and provide a one-sentence conviction rating.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Validation Error: {str(e)}"
