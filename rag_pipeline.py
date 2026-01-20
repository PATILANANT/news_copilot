from typing import List, Dict, Any
import json
from dataclasses import dataclass
from vector_store import VectorStore
from data_fetcher import DataFetcher
import asyncio

@dataclass
class RAGResponse:
    answer: str
    bullet_points: List[str]
    references: List[Dict[str, str]]
    sources: List[str]

class RAGPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.data_fetcher = DataFetcher()
    
    async def update_knowledge_base(self, query: str = None):
        """Update the knowledge base with fresh data"""
        print("🔄 Updating knowledge base with fresh data...")
        
        if query:
            search_query = query
        else:
            search_query = "business investment market news today"
        
        # Fetch fresh data
        fresh_data = await self.data_fetcher.fetch_all_sources(search_query)
        
        # Clear old data and add fresh data
        self.vector_store.clear()  # CHANGED from clear_collection() to clear()
        self.vector_store.add_documents(fresh_data)
        
        print(f"✅ Updated knowledge base with {len(fresh_data)} documents")
        return fresh_data
    
    def format_response(self, query: str, search_results: List[Dict]) -> RAGResponse:
        """Format the response in structured way"""
        
        # Extract information from search results
        sources_used = []
        all_bullet_points = []
        references = []
        
        for result in search_results:
            content = result["content"]
            metadata = result["metadata"]
            
            # Create bullet points from content (simplified extraction)
            lines = content.split('\n')
            for line in lines[:3]:  # Take first 3 lines as bullet points
                if len(line.strip()) > 20:  # Only meaningful lines
                    all_bullet_points.append(f"• {line.strip()}")
            
            # Add to references
            references.append({
                "title": metadata.get("title", "Untitled"),
                "url": metadata.get("url", ""),
                "source": metadata.get("source", "Unknown"),
                "timestamp": metadata.get("timestamp", "")
            })
            
            sources_used.append(metadata.get("source", "Unknown"))
        
        # Remove duplicate bullet points
        unique_bullet_points = []
        seen = set()
        for point in all_bullet_points:
            if point not in seen:
                seen.add(point)
                unique_bullet_points.append(point)
        
        # Generate comprehensive answer
        if unique_bullet_points:
            bullet_points_text = chr(10).join(unique_bullet_points[:5])
        else:
            bullet_points_text = "• No specific points found in the current data."
        
        answer = f"""Based on the latest information about {query}, here's what I found:

📊 **Key Insights:**
{bullet_points_text}

💡 **Summary:**
The current market shows various trends and opportunities. It's important to consider multiple sources and perform due diligence before making investment decisions.

⚠️ **Disclaimer:** This information is for educational purposes only and not financial advice."""

        return RAGResponse(
            answer=answer,
            bullet_points=unique_bullet_points[:10],  # Limit to 10 bullet points
            references=references[:5],  # Limit to 5 references
            sources=list(set(sources_used))
        )
    
    async def query(self, user_query: str, use_fresh_data: bool = True) -> RAGResponse:
        """Main query method"""
        
        if use_fresh_data:
            # Update with fresh data related to query
            await self.update_knowledge_base(user_query)
        
        # Search for relevant information
        search_results = self.vector_store.search(user_query, k=5)  # CHANGED n_results to k
        
        if not search_results:
            return RAGResponse(
                answer="No relevant information found in our current knowledge base.",
                bullet_points=[],
                references=[],
                sources=[]
            )
        
        # Format response
        return self.format_response(user_query, search_results)