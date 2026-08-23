from retriever import get_mmr_retriever

from redundant_filter import (
    remove_redundant_documents,
)

from contextual_compression import compress_documents


# ============================================================
# RETRIEVER
# ============================================================

retriever = get_mmr_retriever(
    k=5,
    fetch_k=20,
    lambda_mult=0.5,
)


questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
]


for question in questions:

    print("\n")
    print("=" * 70)
    print(
        f"QUESTION: {question}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # MMR
    # --------------------------------------------------------

    documents = retriever.invoke(
        question
    )

    print(
        f"\nMMR documents: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # Redundancy filtering
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Contextual compression
    # --------------------------------------------------------

    compressed_documents = (
        compress_documents(
            question,
            filtered_documents,
        )
    )

    print(
        f"After compression: "
        f"{len(compressed_documents)}"
    )

    # --------------------------------------------------------
    # Display compressed context
    # --------------------------------------------------------

    for index, document in enumerate(
        compressed_documents,
        start=1,
    ):

        print("\n")
        print(
            "--- COMPRESSED RESULT",
            index,
            "---",
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
            document.page_content
        )