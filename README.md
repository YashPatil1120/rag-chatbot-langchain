# 📚 RAG Chatbot with LangChain

A multi-document **Retrieval-Augmented Generation (RAG) chatbot** built with Python, LangChain, ChromaDB, Cohere, OpenRouter and Streamlit.

The application allows users to upload **PDF, DOCX and TXT documents**, build a searchable knowledge base, and ask natural-language questions. Instead of relying only on the LLM's general knowledge, the system retrieves relevant information from the uploaded documents and generates answers grounded in that context.

## ✨ Features

- 📄 PDF, DOCX and TXT document ingestion
- 🔍 Semantic vector search using ChromaDB
- 🎯 MMR (Maximum Marginal Relevance) retrieval
- ♻️ Redundant document/chunk filtering
- 🏆 Cohere-based relevance reranking
- ✂️ Contextual compression
- ↕️ Long-context document reordering
- 💬 Conversation-aware question rewriting
- 📚 Document-specific retrieval
- 🛡️ Grounded answers using retrieved context only
- 🔎 Source and retrieval evidence
- 🖥️ Clean and minimal Streamlit interface
- 🔐 Environment-based API key management
- 🚫 Duplicate document detection using file hashing

## 🧠 RAG Pipeline

The application uses multiple retrieval and context-optimization stages instead of directly sending vector-search results to the LLM.

```text
User Question
      ↓
Question Rewriting
      ↓
MMR Retrieval
      ↓
Redundancy Filtering
      ↓
Cohere Reranking
      ↓
Contextual Compression
      ↓
Long-Context Reordering
      ↓
RAG Prompt
      ↓
OpenRouter LLM
      ↓
Grounded Answer + Sources