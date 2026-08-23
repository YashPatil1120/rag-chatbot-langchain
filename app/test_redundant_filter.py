from retriever import get_mmr_retriever

from redundant_filter import (
    remove_redundant_documents,
)


# ============================================================
# TEST RETRIEVER
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
    print("=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)

    documents = retriever.invoke(
        question
    )

    print(
        f"\nBefore filtering: "
        f"{len(documents)} documents"
    )

    filtered_documents = (
        remove_redundant_documents(
            documents,
            similarity_threshold=0.90,
        )
    )

    print(
        f"After filtering: "
        f"{len(filtered_documents)} documents"
    )

    for index, document in enumerate(
        filtered_documents,
        start=1,
    ):

        print("\n--- RESULT", index, "---")

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
            document.page_content[:500]
        )