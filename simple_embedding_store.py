import numpy as np
import os
import pickle
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from config import config
import requests
import json

class SimpleEmbeddingStore:
    def __init__(self):
        # We'll use a simple TF-IDF like approach or use a lightweight model
        self.documents = []
        self.metadata = []
        self.embeddings = []
        self.vocab = {}
        self.load()
    
    def load(self):
        """Load existing data"""
        store_path = os.path.join(config.VECTOR_STORE_PATH, "simple_store.pkl")
        if os.path.exists(store_path):
            try:
                with open(store_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                    self.embeddings = data.get('embeddings', [])
                    self.vocab = data.get('vocab', {})
                print(f"Loaded {len(self.documents)} documents")
            except Exception as e:
                print(f"Error loading store: {e}")
    
    def save(self):
        """Save data to disk"""
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        store_path = os.path.join(config.VECTOR_STORE_PATH, "simple_store.pkl")
        with open(store_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'embeddings': self.embeddings,
                'vocab': self.vocab
            }, f)
        print(f"Saved {len(self.documents)} documents")
    
    def simple_text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to a simple vector using bag of words"""
        words = text.lower().split()
        
        # Build vocabulary if needed
        for word in words:
            if word not in self.vocab:
                self.vocab[word] = len(self.vocab)
        
        # Create vector
        vector = np.zeros(len(self.vocab))
        for word in words:
            if word in self.vocab:
                vector[self.vocab[word]] += 1
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to store"""
        if not documents:
            return
        
        for doc in documents:
            # Combine title and content
            text = f"{doc['title']} {doc['content']}"
            
            if len(text.strip()) < 20:
                continue
            
            # Generate simple embedding
            embedding = self.simple_text_to_vector(text)
            
            self.documents.append(text)
            self.metadata.append({
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "source": doc.get("source", ""),
                "timestamp": doc.get("timestamp", datetime.now().isoformat())
            })
            self.embeddings.append(embedding)
        
        self.save()
        print(f"Added {len(documents)} documents, total: {len(self.documents)}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity"""
        if not self.documents:
            return []
        
        # Convert query to vector
        query_vector = self.simple_text_to_vector(query)
        
        # Calculate similarities
        similarities = []
        for i, doc_vector in enumerate(self.embeddings):
            if len(doc_vector) > 0 and len(query_vector) > 0:
                # Ensure vectors have same dimensions
                max_dim = max(len(doc_vector), len(query_vector))
                doc_vec_padded = np.zeros(max_dim)
                query_vec_padded = np.zeros(max_dim)
                
                doc_vec_padded[:len(doc_vector)] = doc_vector
                query_vec_padded[:len(query_vector)] = query_vector
                
                # Calculate cosine similarity
                dot_product = np.dot(doc_vec_padded, query_vec_padded)
                norm_doc = np.linalg.norm(doc_vec_padded)
                norm_query = np.linalg.norm(query_vec_padded)
                
                if norm_doc > 0 and norm_query > 0:
                    similarity = dot_product / (norm_doc * norm_query)
                    similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Format results
        results = []
        for idx, similarity in similarities[:k]:
            results.append({
                "content": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(similarity)
            })
        
        return results
    
    def clear(self):
        """Clear all documents"""
        self.documents = []
        self.metadata = []
        self.embeddings = []
        self.vocab = {}
        self.save()
        print("Cleared all documents")