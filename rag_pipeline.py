from dataclasses import dataclass
from typing import List, Dict
from vector_store import VectorStore
from data_fetcher import DataFetcher
import asyncio
import datetime


@dataclass
class RAGResponse:
    answer: str
    bullet_points: List[str]
    references: List[Dict[str, str]]
    sources: List[str]


class RAGPipeline:
    def __init__(self):
        self.store = VectorStore()
        self.fetcher = DataFetcher()

    async def refresh_knowledge(self, query: str):
        news = await self.fetcher.fetch_all_sources(query)
        self.store.clear()
        self.store.add_documents(news)
        return news

    def _build_context(self, results: List[Dict]) -> str:
        context = ""
        for r in results:
            m = r["metadata"]
            context += (
                f"Source: {m['source']}\n"
                f"Title: {m['title']}\n"
                f"Date: {m['timestamp']}\n"
                f"Content: {r['content']}\n"
                "----\n"
            )
        return context

    def _llm_answer(self, query: str, context: str) -> str:
        """
        🔴 Replace this with OpenAI / Azure / Gemini call
        """
        return f"""
Based on the latest retrieved news:

{context[:1500]}

Summary:
• Market sentiment is mixed with sector-specific movements
• Investors are reacting to macroeconomic and earnings signals
• Volatility remains due to global factors

⚠️ This is not financial advice.
"""

    async def query(self, query: str, use_fresh_data: bool = True) -> RAGResponse:
        if use_fresh_data:
            await self.refresh_knowledge(query)

        results = self.store.search(query, k=5)
        if not results:
            return RAGResponse(
                answer="No relevant news found.",
                bullet_points=[],
                references=[],
                sources=[]
            )

        context = self._build_context(results)
        answer = self._llm_answer(query, context)

        bullets = []
        refs = []
        sources = set()

        for r in results:
            m = r["metadata"]
            bullets.append(m["title"])
            refs.append(m)
            sources.add(m["source"])

        return RAGResponse(
            answer=answer,
            bullet_points=bullets[:5],
            references=refs[:5],
            sources=list(sources)
        )
