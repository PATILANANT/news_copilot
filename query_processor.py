import json
from typing import Dict, Any
from rag_pipeline import RAGPipeline, RAGResponse

class QueryProcessor:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
    
    def format_final_output(self, response: RAGResponse) -> Dict[str, Any]:
        """Format the final output in a structured way"""
        
        # Create structured output
        output = {
            "query_response": response.answer,
            "key_points": response.bullet_points,
            "references": [
                {
                    "source": ref["source"],
                    "title": ref["title"],
                    "url": ref["url"],
                    "date": ref["timestamp"]
                }
                for ref in response.references
            ],
            "metadata": {
                "total_sources": len(response.sources),
                "sources_used": response.sources,
                "total_key_points": len(response.bullet_points)
            }
        }
        
        return output
    
    def display_output(self, output: Dict[str, Any]):
        """Display output in a user-friendly format"""
        
        print("\n" + "="*80)
        print("📈 BUSINESS & INVESTMENT INTELLIGENCE REPORT")
        print("="*80)
        
        print("\n💬 RESPONSE:")
        print("-"*40)
        print(output["query_response"])
        
        print("\n📋 KEY POINTS:")
        print("-"*40)
        for i, point in enumerate(output["key_points"], 1):
            print(f"{i}. {point}")
        
        print("\n📚 REFERENCES:")
        print("-"*40)
        for i, ref in enumerate(output["references"], 1):
            print(f"\n{i}. {ref['title']}")
            print(f"   Source: {ref['source']}")
            print(f"   URL: {ref['url']}")
            print(f"   Date: {ref['date']}")
        
        print("\n" + "="*80)
        print(f"Total Sources: {output['metadata']['total_sources']}")
        print(f"Sources Used: {', '.join(output['metadata']['sources_used'])}")
        print("="*80 + "\n")
    
    async def process_query(self, query: str, use_fresh_data: bool = True) -> Dict[str, Any]:
        """Process user query and return structured response"""
        print(f"\n🔍 Processing query: '{query}'")
        
        # Get response from RAG pipeline
        response = await self.rag_pipeline.query(query, use_fresh_data=use_fresh_data)
        
        # Format output
        output = self.format_final_output(response)
        
        # Display output
        self.display_output(output)
        
        # Also return as dict for programmatic use
        return output
    