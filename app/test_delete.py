from document_store import (
    load_documents,
    delete_document,
)

from vectorstore import (
    delete_document_vectors,
)


TARGET_FILE = "assign3.pdf"


# ==========================================
# Load documents
# ==========================================

documents = load_documents()


# ==========================================
# Find target document
# ==========================================

target_document = next(
    (
        document
        for document in documents
        if document["file_name"] == TARGET_FILE
    ),
    None,
)


if target_document is None:

    print(
        f"Document not found: {TARGET_FILE}"
    )

    exit()


document_id = target_document[
    "document_id"
]


print("\n==============================")
print("DELETE TEST")
print("==============================")


print(
    f"File: {target_document['file_name']}"
)

print(
    f"Document ID: {document_id}"
)

print(
    f"Expected chunks: "
    f"{target_document['chunks']}"
)


# ==========================================
# Delete vectors from ChromaDB
# ==========================================

deleted_chunks = delete_document_vectors(
    document_id
)


print(
    f"\nDeleted vectors: {deleted_chunks}"
)


# ==========================================
# Delete registry entry
# ==========================================

delete_document(
    document_id
)


print(
    "Document removed from documents.json."
)


print("\nDeletion completed.")