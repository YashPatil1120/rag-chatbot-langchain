from langchain_core.documents import Document

from vectorstore import get_vectorstore


print("=" * 70)
print("TESTING CHROMA METADATA")
print("=" * 70)


# ============================================================
# GET VECTORSTORE
# ============================================================

vectorstore = get_vectorstore()


# ============================================================
# CREATE TEST DOCUMENT
# ============================================================

document = Document(
    page_content=(
        "This is a temporary Chroma metadata test."
    ),
    metadata={
        "document_id": "CHROMA-TEST-ID",
        "file_name": "metadata_test.pdf",
        "file_hash": "CHROMA-TEST-HASH",
        "source": "metadata_test.pdf",
        "page": 99,
    },
)


test_id = "metadata-test-document"


# ============================================================
# ADD TO CHROMA
# ============================================================

vectorstore.add_documents(
    documents=[document],
    ids=[test_id],
)


print(
    "\nTest document successfully added."
)


# ============================================================
# READ DIRECTLY FROM CHROMA
# ============================================================

results = vectorstore.get(
    ids=[test_id]
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n" + "=" * 70)
print("CHROMA RESULT")
print("=" * 70)

print(results)


print("\n" + "=" * 70)
print("CHROMA METADATA")
print("=" * 70)

print(
    results["metadatas"][0]
)