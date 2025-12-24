"""
Quick test script to verify RAG retriever functionality

Run this to test the RAG system before full integration.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_retriever import get_retriever


def test_basic_retrieval():
    """Test basic retrieval functionality."""
    print("=" * 60)
    print("Testing RAG Retriever")
    print("=" * 60)
    
    # Get retriever instance
    print("\n1. Initializing retriever...")
    retriever = get_retriever()
    print(f"   ✓ Loaded {len(retriever.menu_items)} menu items")
    
    # Test queries
    test_queries = [
        "Do you have lobster?",
        "What seafood do you have?",
        "Something spicy",
        "Vegetarian options",
        "Popular items",
        "Under $15"
    ]
    
    print("\n2. Testing retrieval queries:")
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = retriever.retrieve_items(query, top_k=3)
        
        if results:
            print(f"   Top 3 results:")
            for i, item in enumerate(results, 1):
                score = item.get('relevance_score', 0)
                name = item.get('item_name', 'Unknown')
                price = item.get('price', 0)
                print(f"      {i}. {name} (${price:.2f}) - Score: {score:.3f}")
        else:
            print("   No results found")
    
    # Test validation
    print("\n3. Testing item validation:")
    
    valid_items = ["House Special Lobster", "Honey Walnut Shrimps w/ Chips"]
    is_valid, invalid = retriever.validate_items(valid_items)
    print(f"   Valid items: {valid_items}")
    print(f"   ✓ Validation passed: {is_valid}")
    
    invalid_items = ["Pizza", "Burger", "House Special Lobster"]
    is_valid, invalid = retriever.validate_items(invalid_items)
    print(f"\n   Mixed items: {invalid_items}")
    print(f"   ✗ Validation failed: {not is_valid}")
    print(f"   Invalid items detected: {invalid}")
    
    print("\n" + "=" * 60)
    print("✓ RAG Retriever test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_basic_retrieval()
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
