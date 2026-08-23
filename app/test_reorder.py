from retriever import get_mmr_retriever

from redundant_filter import (
    remove_redundant_documents,
)

from reorder import reorder_documents


# ============================================================
# QUESTIONS
# ============================================================

questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
]


# ============================================================
# TEST
# ============================================================

for question in questions:

    print("\n")
    print("=" * 70)
    print(
        f"QUESTION: {question}"
    )
    print("=" * 70)

    # ========================================================
    # 1. MMR RETRIEVAL
    # ========================================================

    retriever = get_mmr_retriever(
        k=5,
        fetch_k=20,
        lambda_mult=0.5,
    )

    documents = retriever.invoke(
        question
    )

    print(
        f"\nMMR documents: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # Check metadata after MMR
    # --------------------------------------------------------

    if documents:

        print(
            "\nMetadata after MMR:"
        )

        print(
            documents[0].metadata
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
        f"\nAfter redundancy filter: "
        f"{len(filtered_documents)}"
    )

    # --------------------------------------------------------
    # Check metadata after filtering
    # --------------------------------------------------------

    if filtered_documents:

        print(
            "\nMetadata after redundancy filter:"
        )

        print(
            filtered_documents[0].metadata
        )

    # ========================================================
    # 3. LONG CONTEXT REORDERING
    # ========================================================

    reordered_documents = (
        reorder_documents(
            filtered_documents
        )
    )

    print(
        f"\nAfter reordering: "
        f"{len(reordered_documents)}"
    )

    # --------------------------------------------------------
    # Check metadata after reordering
    # --------------------------------------------------------

    if reordered_documents:

        print(
            "\nMetadata after reordering:"
        )

        print(
            reordered_documents[0].metadata
        )

    # ========================================================
    # 4. DISPLAY FINAL RESULTS
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
            "Source:",
            document.metadata.get(
                "source"
            ),
        )

        print(
            "File Hash:",
            document.metadata.get(
                "file_hash"
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
            document.page_content[:500]
        )