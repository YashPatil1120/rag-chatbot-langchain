from typing import List

from langchain_core.documents import Document
from langchain_cohere import CohereRerank

from config import COHERE_API_KEY


# ============================================================
# COHERE RERANKER
# ============================================================

reranker = CohereRerank(
    model="rerank-v3.5",
    top_n=5,
    cohere_api_key=COHERE_API_KEY,
)


# ============================================================
# RERANK DOCUMENTS
# ============================================================

def rerank_documents(
    question: str,
    documents: List[Document],
    top_n: int = 5,
):
    """
    Rerank retrieved documents using Cohere.

    Args:
        question: User's question.
        documents: Candidate documents from retrieval.
        top_n: Number of final documents to keep.

    Returns:
        Reranked list of LangChain Documents.
    """

    if not documents:
        return []

    reranker.top_n = top_n

    reranked_documents = reranker.compress_documents(
        documents,
        question,
    )

    return reranked_documents