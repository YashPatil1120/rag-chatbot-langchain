import os

from document_store import (
    delete_document,
)

from vectorstore import (
    delete_document_vectors,
)


def remove_document(
    document_id: str,
    file_path: str | None = None,
):

    # ---------------------------------
    # Delete vectors
    # ---------------------------------

    deleted_chunks = delete_document_vectors(
        document_id
    )


    # ---------------------------------
    # Delete registry entry
    # ---------------------------------

    delete_document(
        document_id
    )


    # ---------------------------------
    # Delete physical PDF
    # ---------------------------------

    file_deleted = False

    if file_path and os.path.exists(file_path):

        os.remove(file_path)

        file_deleted = True


    return {
        "deleted_chunks": deleted_chunks,
        "file_deleted": file_deleted,
    }