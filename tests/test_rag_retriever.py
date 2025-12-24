"""
Unit tests for RAG Retriever

Tests retrieval accuracy, hallucination prevention, and validation.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_retriever import RAGRetriever


class TestRAGRetriever:
    """Test suite for RAG retrieval functionality."""
    
    @pytest.fixture
    def retriever(self):
        """Create a retriever instance for testing."""
        return RAGRetriever()
    
    def test_exact_match(self, retriever):
        """Test retrieval of exact item name."""
        results = retriever.retrieve_items("House Special Lobster", top_k=5)
        
        assert len(results) > 0, "Should return results"
        assert results[0]['item_name'] == "House Special Lobster", \
            "First result should be exact match"
    
    def test_semantic_search_spicy(self, retriever):
        """Test semantic understanding of 'spicy' query."""
        results = retriever.retrieve_items("spicy seafood", top_k=10)
        
        assert len(results) > 0, "Should return results"
        
        # Check if results contain items with spicy-related keywords
        item_names = [r['item_name'].lower() for r in results]
        has_spicy_items = any(
            'chili' in name or 'thai' in name or 'spicy' in name
            for name in item_names
        )
        assert has_spicy_items, "Should retrieve items with spicy keywords"
    
    def test_category_retrieval(self, retriever):
        """Test category-based retrieval."""
        results = retriever.retrieve_items("seafood dishes", top_k=10)
        
        assert len(results) > 0, "Should return results"
        
        # Most results should be seafood
        seafood_count = sum(1 for r in results if r.get('category') == 'Seafood')
        assert seafood_count >= 5, "Should return mostly seafood items"
    
    def test_popular_items(self, retriever):
        """Test retrieval of popular items."""
        results = retriever.retrieve_items("what's popular", top_k=10)
        
        assert len(results) > 0, "Should return results"
        
        # Should include some popular items
        popular_count = sum(1 for r in results if r.get('popular'))
        assert popular_count > 0, "Should include popular items"
    
    def test_price_query(self, retriever):
        """Test retrieval based on price mentions."""
        results = retriever.retrieve_items("something under $15", top_k=10)
        
        assert len(results) > 0, "Should return results"
        
        # Should include some items under $15
        affordable_count = sum(1 for r in results if r.get('price', 999) < 15)
        assert affordable_count > 0, "Should include affordable items"
    
    def test_no_results_fallback(self, retriever):
        """Test behavior when query doesn't match anything well."""
        results = retriever.retrieve_items("xyzabc123nonsense", top_k=5)
        
        # Should still return something (best effort)
        assert len(results) > 0, "Should return results even for poor query"
    
    def test_validation_valid_items(self, retriever):
        """Test validation of valid menu items."""
        valid_items = ["House Special Lobster", "Honey Walnut Shrimps w/ Chips"]
        is_valid, invalid = retriever.validate_items(valid_items)
        
        assert is_valid, "Should validate correct items"
        assert len(invalid) == 0, "Should have no invalid items"
    
    def test_validation_invalid_items(self, retriever):
        """Test validation catches hallucinated items."""
        items_with_fake = [
            "House Special Lobster",  # Valid
            "Pizza Margherita",  # Invalid - not on menu
            "Cheeseburger"  # Invalid - not on menu
        ]
        is_valid, invalid = retriever.validate_items(items_with_fake)
        
        assert not is_valid, "Should detect invalid items"
        assert len(invalid) == 2, "Should identify 2 invalid items"
        assert "Pizza Margherita" in invalid
        assert "Cheeseburger" in invalid
    
    def test_validation_case_insensitive(self, retriever):
        """Test validation is case-insensitive."""
        items = ["house special lobster", "HONEY WALNUT SHRIMPS W/ CHIPS"]
        is_valid, invalid = retriever.validate_items(items)
        
        assert is_valid, "Should validate regardless of case"
    
    def test_retrieval_returns_metadata(self, retriever):
        """Test that retrieved items include all necessary metadata."""
        results = retriever.retrieve_items("lobster", top_k=3)
        
        assert len(results) > 0, "Should return results"
        
        # Check first result has required fields
        item = results[0]
        assert 'item_name' in item, "Should have item_name"
        assert 'price' in item, "Should have price"
        assert 'category' in item, "Should have category"
        assert 'description' in item, "Should have description"
        assert 'relevance_score' in item, "Should have relevance_score"
    
    def test_top_k_limit(self, retriever):
        """Test that top_k parameter is respected."""
        results = retriever.retrieve_items("menu items", top_k=3)
        
        assert len(results) <= 3, "Should return at most top_k items"
    
    def test_different_queries_different_results(self, retriever):
        """Test that different queries return different results."""
        seafood_results = retriever.retrieve_items("seafood", top_k=5)
        chicken_results = retriever.retrieve_items("chicken", top_k=5)
        
        seafood_names = {r['item_name'] for r in seafood_results}
        chicken_names = {r['item_name'] for r in chicken_results}
        
        # Results should be mostly different
        overlap = len(seafood_names & chicken_names)
        assert overlap < 3, "Different queries should return mostly different results"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
