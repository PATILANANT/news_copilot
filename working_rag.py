import asyncio
import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any

class WorkingRAG:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_simple_news(self, query: str = "business") -> List[Dict]:
        """Simple news fetcher"""
        news_items = []
        
        try:
            # Simple RSS feeds that work
            feeds = [
                ("https://feeds.finance.yahoo.com/rss/2.0/headline?s=&region=US&lang=en-US", "Yahoo Finance"),
                ("https://www.investing.com/rss/news_301.rss", "Investing.com"),
            ]
            
            for feed_url, source in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        news_items.append({
                            "title": entry.get("title", "No title"),
                            "content": entry.get("summary", entry.get("title", "")),
                            "url": entry.get("link", "#"),
                            "source": source,
                            "timestamp": entry.get("published", datetime.now().isoformat())
                        })
                except Exception as e:
                    print(f"Warning: Could not fetch from {source}: {e}")
                    continue
            
            # Try Google News
            try:
                google_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(google_url)
                for entry in feed.entries[:5]:
                    news_items.append({
                        "title": entry.get("title", "No title"),
                        "content": entry.get("summary", entry.get("title", "")),
                        "url": entry.get("link", "#"),
                        "source": "Google News",
                        "timestamp": entry.get("published", datetime.now().isoformat())
                    })
            except:
                pass
                
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return news_items[:10]  # Return max 10 items
    
    def simple_search(self, query: str, news_items: List[Dict]) -> List[Dict]:
        """Simple keyword search"""
        query_lower = query.lower()
        results = []
        
        for item in news_items:
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            
            # Check if query words are in title or content
            score = 0
            for word in query_lower.split():
                if word in title:
                    score += 2
                if word in content:
                    score += 1
            
            if score > 0:
                results.append({
                    "item": item,
                    "score": score
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["item"] for r in results[:5]]
    
    def format_response(self, query: str, results: List[Dict]) -> str:
        """Format the response"""
        if not results:
            return f"No results found for '{query}'. Try a different search term."
        
        response = f"📈 Results for: {query}\n"
        response += "="*50 + "\n\n"
        
        for i, item in enumerate(results, 1):
            response += f"{i}. {item['title']}\n"
            response += f"   📍 Source: {item['source']}\n"
            response += f"   📝 {item['content'][:150]}...\n"
            response += f"   🔗 {item['url']}\n"
            response += f"   🕐 {item['timestamp'][:10]}\n\n"
        
        response += "="*50
        response += "\n💡 Tip: Always verify information from multiple sources."
        
        return response
    
    async def process_query(self, query: str):
        """Main processing method"""
        print(f"\n🔍 Searching for: '{query}'")
        
        # Fetch news
        news = await self.fetch_simple_news(query)
        
        if not news:
            print("❌ No news found. Check your internet connection.")
            return
        
        # Search
        results = self.simple_search(query, news)
        
        # Format and display
        response = self.format_response(query, results)
        print(response)

async def main():
    rag = WorkingRAG()
    
    print("\n" + "="*50)
    print("🤖 SIMPLE NEWS RAG SYSTEM")
    print("="*50)
    print("\nType your query (business, stocks, investment, etc.)")
    print("Type 'quit' to exit")
    
    while True:
        query = input("\n🔍 Your query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if query:
            await rag.process_query(query)

if __name__ == "__main__":
    asyncio.run(main())