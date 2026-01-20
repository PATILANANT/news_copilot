from rag_pipeline import RAGPipeline
from datetime import datetime


class QueryProcessor:
    def __init__(self):
        self.pipeline = RAGPipeline()

    async def process_query(self, query: str):
        response = await self.pipeline.query(query)

        print("\n" + "=" * 80)
        print("📊 BUSINESS & INVESTMENT NEWS COPILOT")
        print("=" * 80)

        print("\n🧠 ANSWER:")
        print(response.answer)

        print("\n📌 KEY POINTS:")
        for i, b in enumerate(response.bullet_points, 1):
            print(f"{i}. {b}")

        print("\n📚 SOURCES:")
        for r in response.references:
            print(f"- {r['source']} | {r['title']}")

        print("\n🕒 Last Updated:", datetime.utcnow().isoformat(), "UTC")
        print("=" * 80)
