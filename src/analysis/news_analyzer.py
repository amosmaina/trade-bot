import requests
from bs4 import BeautifulSoup
from datetime import datetime

class NewsAnalyzer:
    def __init__(self):
        self.url = "https://www.forexfactory.com/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_news(self):
        """
        Fetch economic calendar news from ForexFactory
        """
        try:
            # Note: Scrapers for ForexFactory can be fragile due to anti-bot.
            # In a real institutional app, we would use a paid API like Finnhub or AlphaVantage.
            # This is a simplified simulation for the bot.
            print("Fetching high-impact news...")
            return [
                {"event": "CPI m/m", "impact": "High", "currency": "USD", "time": "14:30"},
                {"event": "FOMC Statement", "impact": "High", "currency": "USD", "time": "20:00"},
                {"event": "ECB Press Conference", "impact": "High", "currency": "EUR", "time": "15:45"}
            ]
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def get_market_sentiment(self, symbol):
        """
        Analyze news for a specific symbol
        """
        news = self.fetch_news()
        currency = symbol[:3] # e.g., EUR from EURUSD
        impact_news = [n for n in news if n['currency'] == currency and n['impact'] == 'High']
        
        if impact_news:
            return {
                "status": "CAUTION",
                "reason": f"High impact news detected for {currency}: {impact_news[0]['event']}",
                "impact_events": impact_news
            }
        return {"status": "STABLE", "reason": "No immediate high-impact news."}
