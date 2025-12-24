"""
RAG Retriever Module - Hybrid Search for Menu Items

This module implements Retrieval-Augmented Generation (RAG) for menu items using:
1. Semantic search with sentence-transformers embeddings
2. BM25 keyword search for exact matches
3. Rank fusion to combine results

This prevents hallucinations by ensuring only real menu items are retrieved.
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi
import config


class RAGRetriever:
    """Hybrid retrieval system for menu items using semantic + keyword search."""
    
    def __init__(self):
        """Initialize the retriever with embedding model and indexes."""
        print("Initializing RAG Retriever...")
        
        # Load lightweight embedding model (all-MiniLM-L6-v2: 80MB, fast)
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Storage for menu items and their embeddings
        self.menu_items: List[Dict[str, Any]] = []
        self.item_chunks: List[str] = []  # Contextual text chunks
        self.embeddings: np.ndarray = None
        self.faiss_index = None
        self.bm25_index = None
        
        # Index the menu on initialization
        self._load_and_index_menu()
        
        print(f"RAG Retriever initialized with {len(self.menu_items)} menu items")
    
    def _load_and_index_menu(self):
        """Load menu from JSON and build search indexes."""
        try:
            with open(config.MENU_PATH, 'r', encoding='utf-8') as f:
                menu_data = json.load(f)
                self.menu_items = menu_data.get('items', [])
            
            if not self.menu_items:
                print("Warning: No menu items found!")
                return
            
            # Build contextual chunks for each item
            self.item_chunks = [self._create_contextual_chunk(item) for item in self.menu_items]
            
            # Build semantic search index (FAISS)
            self._build_semantic_index()
            
            # Build keyword search index (BM25)
            self._build_bm25_index()
            
        except Exception as e:
            print(f"Error loading menu: {e}")
            self.menu_items = []
            self.item_chunks = []
    
    def _create_contextual_chunk(self, item: Dict[str, Any]) -> str:
        """
        Create a rich, contextual text chunk for a menu item.
        
        This follows Anthropic's "Contextual Retrieval" approach:
        Prepend context to each chunk to improve retrieval accuracy.
        """
        restaurant_info = "Garlic & Chives restaurant in Garden Grove, CA"
        
        chunk = f"""This menu item is from {restaurant_info}.
Category: {item.get('category', 'Other')}
Item Name: {item.get('item_name', 'Unknown')}
Price: ${item.get('price', 0):.2f}
{f"[POPULAR ITEM]" if item.get('popular') else ""}
Description: {item.get('description', '')}
"""
        return chunk.strip()
    
    def _build_semantic_index(self):
        """Build FAISS index for semantic similarity search."""
        print("Building semantic search index...")
        
        # Generate embeddings for all chunks
        self.embeddings = self.embedding_model.encode(
            self.item_chunks,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Create FAISS index (L2 distance)
        dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(self.embeddings)
        
        print(f"Semantic index built with {len(self.embeddings)} embeddings")
    
    def _build_bm25_index(self):
        """Build BM25 index for keyword search."""
        print("Building BM25 keyword index...")
        
        # Tokenize chunks (simple whitespace tokenization)
        tokenized_chunks = [chunk.lower().split() for chunk in self.item_chunks]
        
        # Build BM25 index
        self.bm25_index = BM25Okapi(tokenized_chunks)
        
        print("BM25 index built")
    
    def retrieve_items(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.6,
        bm25_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Retrieve menu items using hybrid search (semantic + keyword).
        
        Args:
            query: User's search query
            top_k: Number of items to return
            semantic_weight: Weight for semantic search scores (0-1)
            bm25_weight: Weight for BM25 scores (0-1)
        
        Returns:
            List of menu items with relevance scores
        """
        if not self.menu_items:
            return []
        
        # 1. Semantic search
        semantic_results = self._semantic_search(query, top_k=min(10, len(self.menu_items)))
        
        # 2. BM25 keyword search
        bm25_results = self._bm25_search(query, top_k=min(10, len(self.menu_items)))
        
        # 3. Rank fusion (combine scores)
        fused_results = self._rank_fusion(
            semantic_results,
            bm25_results,
            semantic_weight,
            bm25_weight
        )
        
        # 4. Return top K with metadata
        return fused_results[:top_k]
    
    def _semantic_search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        """
        Perform semantic similarity search using FAISS.
        
        Returns:
            List of (item_index, similarity_score) tuples
        """
        if self.faiss_index is None:
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        )
        
        # Search FAISS index (returns distances, we convert to similarity)
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        
        # Convert L2 distances to similarity scores (inverse)
        # Lower distance = higher similarity
        similarities = 1 / (1 + distances[0])
        
        return list(zip(indices[0], similarities))
    
    def _bm25_search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        """
        Perform BM25 keyword search.
        
        Returns:
            List of (item_index, bm25_score) tuples
        """
        if self.bm25_index is None:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores for all documents
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [(idx, scores[idx]) for idx in top_indices]
    
    def _rank_fusion(
        self,
        semantic_results: List[Tuple[int, float]],
        bm25_results: List[Tuple[int, float]],
        semantic_weight: float,
        bm25_weight: float
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and BM25 results using weighted score fusion.
        
        Returns:
            List of menu items sorted by fused score
        """
        # Normalize scores to [0, 1] range
        def normalize_scores(results: List[Tuple[int, float]]) -> Dict[int, float]:
            if not results:
                return {}
            
            scores = [score for _, score in results]
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score == min_score:
                return {idx: 1.0 for idx, _ in results}
            
            return {
                idx: (score - min_score) / (max_score - min_score)
                for idx, score in results
            }
        
        semantic_normalized = normalize_scores(semantic_results)
        bm25_normalized = normalize_scores(bm25_results)
        
        # Combine scores
        all_indices = set(semantic_normalized.keys()) | set(bm25_normalized.keys())
        
        fused_scores = {}
        for idx in all_indices:
            semantic_score = semantic_normalized.get(idx, 0.0)
            bm25_score = bm25_normalized.get(idx, 0.0)
            
            fused_scores[idx] = (
                semantic_weight * semantic_score +
                bm25_weight * bm25_score
            )
        
        # Sort by fused score
        sorted_indices = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return menu items with scores
        results = []
        for idx, score in sorted_indices:
            item = self.menu_items[idx].copy()
            item['relevance_score'] = score
            results.append(item)
        
        return results
    
    def validate_items(self, item_names: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that all item names exist in the menu.
        
        Args:
            item_names: List of item names to validate
        
        Returns:
            (all_valid, invalid_items) tuple
        """
        valid_names = {item['item_name'].lower() for item in self.menu_items}
        invalid = [name for name in item_names if name.lower() not in valid_names]
        
        return (len(invalid) == 0, invalid)


# Global singleton instance
_retriever_instance = None

def get_retriever() -> RAGRetriever:
    """Get or create the global RAG retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = RAGRetriever()
    return _retriever_instance
