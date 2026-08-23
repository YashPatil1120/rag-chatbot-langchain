from loaders import load_document
from splitter import split_documents


PDF_PATH = "data/MongoDB Handbook.pdf"


print("=" * 70)
print("TESTING METADATA BEFORE CHROMA")
print("=" * 70)


# ============================================================
# 1. LOAD DOCUMENT
# ============================================================

documents = load_document(
    PDF_PATH
)

print(
    f"\nLoaded documents: {len(documents)}"
)


# ============================================================
# 2. SPLIT DOCUMENT
# ============================================================

chunks = split_documents(
    documents
)

print(
    f"Created chunks: {len(chunks)}"
)


# ============================================================
# 3. SIMULATE INGEST.PY METADATA
# ============================================================

test_document_id = "TEST-DOCUMENT-ID"

test_filename = "MongoDB Handbook.pdf"

test_hash = "TEST-FILE-HASH"


for chunk in chunks:

    chunk.metadata["document_id"] = (
        test_document_id
    )

    chunk.metadata["file_name"] = (
        test_filename
    )

    chunk.metadata["source"] = (
        test_filename
    )

    chunk.metadata["file_hash"] = (
        test_hash
    )


# ============================================================
# 4. DISPLAY METADATA
# ============================================================

print("\n" + "=" * 70)
print("FIRST CHUNK METADATA")
print("=" * 70)

print(
    chunks[0].metadata
)


# ============================================================
# 5. CHECK IMPORTANT FIELDS
# ============================================================

metadata = chunks[0].metadata


print("\n" + "=" * 70)
print("CUSTOM METADATA CHECK")
print("=" * 70)


print(
    "document_id:",
    metadata.get("document_id")
)

print(
    "file_name:",
    metadata.get("file_name")
)

print(
    "file_hash:",
    metadata.get("file_hash")
)

print(
    "source:",
    metadata.get("source")
)

print(
    "page:",
    metadata.get("page")
)