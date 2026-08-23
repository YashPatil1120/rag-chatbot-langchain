from retriever import get_mmr_retriever

from redundant_filter import (
    remove_redundant_documents,
)

from reranker import (
    rerank_documents,
)

from reorder import (
    reorder_documents,
)


# ============================================================
# QUESTIONS
# ============================================================

questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
]


# ============================================================
# TEST EACH QUESTION
# ============================================================

for question in questions:

    print("\n")
    print("=" * 70)
    print(f"QUESTION: {question}")
    print("=" * 70)

    # ========================================================
    # 1. MMR RETRIEVAL
    # ========================================================

    retriever = get_mmr_retriever(
        k=15,
        fetch_k=30,
        lambda_mult=0.5,
    )

    documents = retriever.invoke(
        question
    )

    print(
        f"\nMMR documents: {len(documents)}"
    )


    # ========================================================
    # 2. REDUNDANCY FILTER
    # ========================================================

    filtered_documents = (
        remove_redundant_documents(
            documents,
            similarity_threshold=0.90,
        )
    )

    print(
        f"After redundancy filter: "
        f"{len(filtered_documents)}"
    )


    # ========================================================
    # 3. COHERE RERANKING
    # ========================================================

    reranked_documents = rerank_documents(
        question=question,
        documents=filtered_documents,
        top_n=5,
    )

    print(
        f"After Cohere reranking: "
        f"{len(reranked_documents)}"
    )


    # ========================================================
    # 4. LONG-CONTEXT REORDER
    # ========================================================

    reordered_documents = reorder_documents(
        reranked_documents
    )

    print(
        f"After long-context reorder: "
        f"{len(reordered_documents)}"
    )


    # ========================================================
    # 5. DISPLAY RESULTS
    # ========================================================

    for index, document in enumerate(
        reordered_documents,
        start=1,
    ):

        print("\n")
        print(
            f"--- RESULT {index} ---"
        )

        print(
            "File:",
            document.metadata.get(
                "file_name"
            ),
        )

        print(
            "Document ID:",
            document.metadata.get(
                "document_id"
            ),
        )

        print(
            "Page:",
            document.metadata.get(
                "page"
            ),
        )

        print(
            "Content:"
        )

        print(
            document.page_content[:700]
        )