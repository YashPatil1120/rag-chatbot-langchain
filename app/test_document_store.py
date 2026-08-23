from ingest import calculate_file_hash
from document_store import (
    find_document_by_hash,
    add_document,
)


pdf_path = "data/MongoDB Handbook.pdf"


# Calculate hash
file_hash = calculate_file_hash(pdf_path)

print("File hash:")
print(file_hash)


# Check whether this hash already exists
existing = find_document_by_hash(file_hash)

print("\nExisting document:")
print(existing)


# If it doesn't exist, add a test record
if existing is None:

    test_document = {
        "document_id": "test-document-001",
        "file_name": "MongoDB Handbook.pdf",
        "file_hash": file_hash,
        "pages": 13,
        "chunks": 27,
    }

    add_document(test_document)

    print("\nDocument added to registry.")

else:

    print("\nDocument already exists in registry.")