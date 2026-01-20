import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import hashlib
from datetime import datetime
from config import config

class VectorStore:
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Load existing index if available
        self.load_index()
    
    def load_index(self):
        """Load existing FAISS index and documents"""
        index_path = os.path.join(config.VECTOR_STORE_PATH, "index.faiss")
        meta_path = os.path.join(config.VECTOR_STORE_PATH, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(meta_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(meta_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                print(f"Loaded {len(self.documents)} documents from existing index")
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self.create_new_index()
        else:
            self.create_new_index()
    
    def create_new_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.metadata = []
        print("Created new FAISS index")
    
    def save_index(self):
        """Save FAISS index and documents"""
        # Create directory if it doesn't exist
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(config.VECTOR_STORE_PATH, "index.faiss")
        faiss.write_index(self.index, index_path)
        
        # Save documents and metadata
        meta_path = os.path.join(config.VECTOR_STORE_PATH, "metadata.pkl")
        with open(meta_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        print(f"Saved {len(self.documents)} documents to {config.VECTOR_STORE_PATH}")
    
    def generate_id(self, text: str) -> str:
        """Generate unique ID for document"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        if not documents:
            return
        
        new_embeddings = []
        new_documents = []
        new_metadata = []
        
        for doc in documents:
            # Combine title and content for embedding
            text = f"{doc['title']}\n{doc['content']}"
            
            # Skip if document is too short
            if len(text.strip()) < 50:
                continue
            
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            embedding = embedding.reshape(1, -1).astype('float32')
            
            # Add to collections
            new_embeddings.append(embedding)
            new_documents.append(text)
            new_metadata.append({
                "title": doc.get("title", ""),
                "content": doc.get("content", ""),
                "url": doc.get("url", ""),
                "source": doc.get("source", ""),
                "timestamp": doc.get("timestamp", datetime.now().isoformat())
            })
        
        if new_embeddings:
            # Convert list of embeddings to numpy array
            all_embeddings = np.vstack(new_embeddings)
            
            # Add to FAISS index
            if self.index.ntotal == 0:
                self.index.add(all_embeddings)
            else:
                # Concatenate with existing embeddings
                existing_embeddings = self.index.reconstruct_n(0, self.index.ntotal)
                combined_embeddings = np.vstack([existing_embeddings, all_embeddings])
                
                # Create new index with combined embeddings
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.index.add(combined_embeddings)
            
            # Add to documents and metadata
            self.documents.extend(new_documents)
            self.metadata.extend(new_metadata)
            
            # Save the updated index
            self.save_index()
            
            print(f"Added {len(new_documents)} new documents to vector store")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search in index
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents) and idx >= 0:
                # Convert L2 distance to similarity score (higher is better)
                similarity = 1 / (1 + distances[0][i])
                
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": similarity
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def clear(self):
        """Clear all documents from vector store"""
        self.create_new_index()
        self.documents = []
        self.metadata = []
        self.save_index()
        print("Cleared all documents from vector store")