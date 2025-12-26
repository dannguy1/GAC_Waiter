import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.rag_retriever import get_retriever

def test_bio_retrieval():
    retriever = get_retriever()
    queries = [
        "Who is the owner?",
        "Tell me about the restaurant",
        "Where are you located?"
    ]
    
    print(f"Total Items Indexed: {len(retriever.menu_items)}")
    
    for q in queries:
        print(f"\nQuery: {q}")
        results = retriever.retrieve_items(q, top_k=2)
        for item in results:
             topic = item.get('topic', item.get('item_name'))
             print(f"- {topic} ({item.get('type')})")

if __name__ == "__main__":
    test_bio_retrieval()
