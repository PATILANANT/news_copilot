import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Test only the data fetching part"""
    try:
        from data_fetcher import DataFetcher
        
        print("🧪 Testing Data Fetcher...")
        fetcher = DataFetcher()
        
        print("🔍 Fetching business news...")
        data = await fetcher.fetch_all_sources("business news")
        
        print(f"\n✅ Success! Found {len(data)} news items")
        
        if data:
            print("\n📰 Sample News Items:")
            print("-" * 50)
            for i, item in enumerate(data[:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   Source: {item['source']}")
                print(f"   Preview: {item['content'][:100]}...")
        
        print(f"\n🎉 Data fetching works! Total items: {len(data)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())