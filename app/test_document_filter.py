from retriever import get_retriever


# ============================================================
# TEST DOCUMENT IDS
# ============================================================

MONGODB_ID = "40ca4a5d-a844-4a09-a780-c81b7ff39a77"

FINANCE_ID = "87e01f27-1cf1-4723-93d5-66f8b4b9cccb"


# ============================================================
# TEST 1 — FINANCIAL MANAGEMENT DOCUMENT ONLY
# ============================================================

print("\n")
print("=" * 60)
print("TEST 1 — FINANCIAL MANAGEMENT ONLY")
print("=" * 60)

retriever = get_retriever(
    k=5,
    document_id=FINANCE_ID,
)

documents = retriever.invoke(
    "What is Simple Interest?"
)

print(
    f"Retrieved documents: {len(documents)}"
)

for i, document in enumerate(
    documents,
    start=1,
):

    print(
        f"\n--- RESULT {i} ---"
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
        document.page_content[:300]
    )


# ============================================================
# TEST 2 — MONGODB DOCUMENT ONLY
# ============================================================

print("\n")
print("=" * 60)
print("TEST 2 — MONGODB ONLY")
print("=" * 60)

retriever = get_retriever(
    k=5,
    document_id=MONGODB_ID,
)

documents = retriever.invoke(
    "What is MongoDB?"
)

print(
    f"Retrieved documents: {len(documents)}"
)

for i, document in enumerate(
    documents,
    start=1,
):

    print(
        f"\n--- RESULT {i} ---"
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
        document.page_content[:300]
    )


# ============================================================
# TEST 3 — NON-EXISTENT DOCUMENT
# ============================================================

print("\n")
print("=" * 60)
print("TEST 3 — NON-EXISTENT DOCUMENT")
print("=" * 60)

retriever = get_retriever(
    k=5,
    document_id="does-not-exist",
)

documents = retriever.invoke(
    "What is MongoDB?"
)

print(
    f"Retrieved documents: {len(documents)}"
)