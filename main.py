import asyncio
from query_processor import QueryProcessor


async def main():
    qp = QueryProcessor()
    while True:
        q = input("\n🔍 Ask about business or investments: ")
        if q.lower() in ("exit", "quit"):
            break
        await qp.process_query(q)


if __name__ == "__main__":
    asyncio.run(main())
