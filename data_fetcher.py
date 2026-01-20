import requests
import feedparser
import yfinance as yf
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from newspaper import Article
from config import config  # CHANGED from settings to config

class DataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # Free APIs - No API key required
    async def fetch_market_news(self, query: str = "business investment") -> List[Dict]:
        """Fetch market news using free APIs"""
        sources = []
        
        try:
            # RSS Feeds (Free)
            rss_feeds = [
                "https://feeds.finance.yahoo.com/rss/2.0/headline?s=&region=US&lang=en-US",
                "https://www.investing.com/rss/news_301.rss"  # Removed broken feed
            ]
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        sources.append({
                            "title": entry.get("title", ""),
                            "content": entry.get("summary", ""),
                            "url": entry.get("link", ""),
                            "source": feed_url,
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error fetching market news: {e}")
        
        return sources
    
    async def fetch_yahoo_finance(self, symbol: str = None) -> List[Dict]:
        """Fetch data from Yahoo Finance (free)"""
        data = []
        try:
            if symbol:
                stock = yf.Ticker(symbol)
                info = stock.info
                news = stock.news
                
                # Add basic info if available
                if 'currentPrice' in info:
                    data.append({
                        "title": f"{symbol} Stock Info",
                        "content": f"Current Price: {info.get('currentPrice', 'N/A')}, "
                                  f"Market Cap: {info.get('marketCap', 'N/A')}, "
                                  f"PE Ratio: {info.get('trailingPE', 'N/A')}",
                        "url": f"https://finance.yahoo.com/quote/{symbol}",
                        "source": "Yahoo Finance",
                        "timestamp": datetime.now().isoformat()
                    })
                
                if news:
                    for item in news[:3]:
                        data.append({
                            "title": item.get('title', ''),
                            "content": item.get('summary', ''),
                            "url": item.get('link', ''),
                            "source": "Yahoo Finance News",
                            "timestamp": datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"Error fetching Yahoo Finance data: {e}")
        
        return data
    
    async def fetch_google_news(self, query: str = "business investment") -> List[Dict]:
        """Fetch Google News (free through RSS)"""
        data = []
        try:
            # Google News RSS
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:10]:
                data.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": "Google News",
                    "timestamp": entry.get("published", datetime.now().isoformat())
                })
        except Exception as e:
            print(f"Error fetching Google News: {e}")
        
        return data
    
    async def fetch_investing_com(self) -> List[Dict]:
        """Fetch from Investing.com RSS"""
        data = []
        try:
            urls = [
                "https://www.investing.com/rss/news_25.rss",  # US Markets
                "https://www.investing.com/rss/news_301.rss", # Stock Markets
            ]
            
            for url in urls:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    data.append({
                        "title": entry.get("title", ""),
                        "content": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "source": "Investing.com",
                        "timestamp": entry.get("published", datetime.now().isoformat())
                    })
        except Exception as e:
            print(f"Error fetching Investing.com: {e}")
        
        return data
    
    async def fetch_all_sources(self, query: str = "business investment news") -> List[Dict]:
        """Fetch data from all available sources"""
        all_data = []
        
        # Create tasks for all sources
        tasks = [
            self.fetch_market_news(query),
            self.fetch_yahoo_finance("^GSPC"),  # S&P 500
            self.fetch_google_news(query),
            self.fetch_investing_com()
        ]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_data = []
        for item in all_data:
            if item.get('url') and item.get('url') not in seen_urls:
                seen_urls.add(item.get('url'))
                unique_data.append(item)
        
        return unique_data[:config.MAX_RESULTS]  # CHANGED from settings to config