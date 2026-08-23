import hashlib
from pathlib import Path
from uuid import uuid4

from loaders import load_document
from splitter import split_documents
from vectorstore import get_vectorstore

from document_store import (
    find_document_by_hash,
    add_document,
)


# ============================================================
# FILE HASH
# ============================================================

def calculate_file_hash(file_path: str):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while chunk := file.read(1024 * 1024):

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# DOCUMENT INGESTION
# ============================================================

def ingest_document(
    file_path: str,
    original_filename: str,
):

    print(
        f"\nStarting ingestion: {original_filename}"
    )

    # ---------------------------------
    # 1. Calculate file hash
    # ---------------------------------

    file_hash = calculate_file_hash(
        file_path
    )

    print(
        f"File hash: {file_hash}"
    )


    # ---------------------------------
    # 2. Check duplicate
    # ---------------------------------

    existing_document = (
        find_document_by_hash(file_hash)
    )

    if existing_document:

        print(
            "Document already exists. "
            "Skipping ingestion."
        )

        return {
            **existing_document,
            "already_exists": True,
        }


    # ---------------------------------
    # 3. Load document
    # ---------------------------------

    documents = load_document(
        file_path
    )

    print(
        f"Loaded document sections/pages: "
        f"{len(documents)}"
    )


    # ---------------------------------
    # 4. Split into chunks
    # ---------------------------------

    chunks = split_documents(
        documents
    )

    print(
        f"Created chunks: {len(chunks)}"
    )


    # ---------------------------------
    # 5. Validate document
    # ---------------------------------

    if not chunks:

        raise ValueError(
            "No usable text was found "
            "in the uploaded document."
        )


    # ---------------------------------
    # 6. Create document ID
    # ---------------------------------

    document_id = str(
        uuid4()
    )


    # ---------------------------------
    # 7. Add metadata
    # ---------------------------------

    file_type = (
        Path(file_path)
        .suffix
        .lower()
        .replace(".", "")
    )

    for chunk in chunks:

        chunk.metadata[
            "document_id"
        ] = document_id

        chunk.metadata[
            "file_name"
        ] = original_filename

        chunk.metadata[
            "source"
        ] = original_filename

        chunk.metadata[
            "file_hash"
        ] = file_hash

        chunk.metadata[
            "file_type"
        ] = file_type


    # ---------------------------------
    # 8. Open ChromaDB
    # ---------------------------------

    vectorstore = get_vectorstore()


    # ---------------------------------
    # 9. Create chunk IDs
    # ---------------------------------

    chunk_ids = [

        f"{document_id}_{i}"

        for i in range(
            len(chunks)
        )

    ]


    # ---------------------------------
    # 10. Add chunks to ChromaDB
    # ---------------------------------

    vectorstore.add_documents(

        documents=chunks,

        ids=chunk_ids,

    )

    print(
        "Successfully added chunks "
        "to ChromaDB."
    )


    # ---------------------------------
    # 11. Create registry record
    # ---------------------------------

    document_record = {

        "document_id":
            document_id,

        "file_name":
            original_filename,

        "file_hash":
            file_hash,

        "file_type":
            file_type,

        "pages":
            len(documents),

        "chunks":
            len(chunks),

    }


    # ---------------------------------
    # 12. Save registry
    # ---------------------------------

    add_document(
        document_record
    )

    print(
        "Document registered successfully."
    )


    # ---------------------------------
    # 13. Return result
    # ---------------------------------

    return {

        **document_record,

        "already_exists":
            False,

    }