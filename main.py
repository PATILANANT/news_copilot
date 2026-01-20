import asyncio
import sys
from query_processor import QueryProcessor
import argparse

async def main():
    parser = argparse.ArgumentParser(description="Business & Investment RAG Pipeline")
    parser.add_argument("--query", type=str, help="Your query about business/investment")
    parser.add_argument("--cached", action="store_true", help="Use cached data instead of fresh fetch")
    args = parser.parse_args()
    
    processor = QueryProcessor()
    
    if args.query:
        # Use provided query
        query = args.query
    else:
        # Interactive mode
        print("\n" + "="*80)
        print("🤖 Business & Investment Intelligence RAG Pipeline")
        print("="*80)
        print("\nEnter your query about business, investments, or markets.")
        print("Type 'quit' or 'exit' to end.")
        print("-"*80)
        
        while True:
            query = input("\n🔍 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                print("Please enter a query.")
                continue
            
            try:
                await processor.process_query(query, use_fresh_data=not args.cached)
            except Exception as e:
                print(f"❌ Error processing query: {e}")
    
    if args.query:
        try:
            await processor.process_query(args.query, use_fresh_data=not args.cached)
        except Exception as e:
            print(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    # For Windows compatibility with asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
    