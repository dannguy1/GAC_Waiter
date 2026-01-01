## RAG Integration (Phase 1)

### Overview
The system now uses **Retrieval-Augmented Generation (RAG)** to ensure menu accuracy and dramatically reduce token usage.

### Architecture

**Module**: `backend/rag_retriever.py`

**Components**:
1. **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (lightweight, fast)
2. **Vector Store**: FAISS (in-memory, CPU-optimized)
3. **Keyword Search**: BM25 algorithm for exact matches
4. **Rank Fusion**: Weighted combination of semantic and keyword results

### How It Works

1. **Indexing** (on startup):
   - Load all menu items from `menu.json`
   - Create contextual chunks with restaurant info, category, price, description
   - Generate embeddings using sentence-transformers
   - Build FAISS index for semantic search
   - Build BM25 index for keyword search

2. **Retrieval** (per query):
   - User query: "Do you have spicy seafood?"
   - Semantic search: Find top 10 similar items by embedding
   - Keyword search: Find top 10 items by BM25 score
   - Rank fusion: Combine results with 60% semantic, 40% keyword weighting
   - Return top 5 most relevant items

3. **Validation** (at checkout):
   - Extract all item names from LLM-generated order
   - Validate each item exists in menu
   - Filter out any hallucinated items
   - Recalculate total if items were removed
   - Log warnings for debugging

### Benefits

- **99% Token Reduction**: 50,000 → 500 tokens per request
- **Hallucination Prevention**: Only real menu items can be retrieved
- **Accuracy**: Hybrid search ensures both semantic and exact matches
- **Flexibility**: Easy to update menu (currently requires restart; Phase 2 enables hot-reload)

### Dependencies

- `sentence-transformers>=3.0.0` - Embedding model
- `faiss-cpu>=1.8.0` - Vector similarity search
- `rank-bm25==0.2.2` - Keyword search

### Future Enhancements (Phase 2 & 3)

**Phase 2 - Production RAG**:
- Persistent vector database (Qdrant/Chroma)
- Hot-reload menu updates via API
- Multi-location support with metadata filtering

**Phase 3 - Smart Recommendations**:
- Context-aware recommendations based on conversation history
- Business logic integration (profit margins, inventory levels)
- Personalization (dietary preferences, allergies)
- A/B testing for recommendation quality
