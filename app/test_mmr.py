from retriever import get_mmr_retriever


# ============================================================
# TEST QUESTIONS
# ============================================================

questions = [

    "What is MongoDB?",

    "What is mongosh?",

    "How does aggregation work?",

    "What is the capital of France?",

]


# ============================================================
# CREATE MMR RETRIEVER
# ============================================================

retriever = get_mmr_retriever(

    k=5,

    fetch_k=20,

    lambda_mult=0.5,

)


# ============================================================
# RUN TESTS
# ============================================================

for question in questions:

    print("\n")
    print("=" * 70)

    print(
        f"QUESTION: {question}"
    )

    print("=" * 70)


    documents = retriever.invoke(
        question
    )


    print(
        f"Retrieved documents: "
        f"{len(documents)}"
    )


    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"\n--- RESULT {index} ---"
        )


        print(
            f"File: "
            f"{document.metadata.get('file_name')}"
        )


        print(
            f"Document ID: "
            f"{document.metadata.get('document_id')}"
        )


        print(
            f"Page: "
            f"{document.metadata.get('page')}"
        )


        print(
            "Content:"
        )


        print(
            document.page_content[:500]
        )

print("\n")
print("=" * 70)
print("DOCUMENT FILTER TEST")
print("=" * 70)


mongodb_document_id = (
    "40ca4a5d-a844-4a09-a780-c81b7ff39a77"
)


filtered_retriever = get_mmr_retriever(

    k=5,

    fetch_k=20,

    lambda_mult=0.5,

    document_id=mongodb_document_id,

)


documents = filtered_retriever.invoke(
    "What is MongoDB?"
)


print(
    f"Retrieved documents: "
    f"{len(documents)}"
)


for index, document in enumerate(
    documents,
    start=1,
):

    print(
        f"\n--- RESULT {index} ---"
    )

    print(
        f"File: "
        f"{document.metadata.get('file_name')}"
    )

    print(
        f"Document ID: "
        f"{document.metadata.get('document_id')}"
    )

    print(
        f"Page: "
        f"{document.metadata.get('page')}"
    )