import json
import os


DOCUMENTS_FILE = "data/documents.json"


def load_documents():

    if not os.path.exists(
        DOCUMENTS_FILE
    ):

        return []

    with open(
        DOCUMENTS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def save_documents(documents):

    os.makedirs(
        "data",
        exist_ok=True,
    )

    with open(
        DOCUMENTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            documents,
            file,
            indent=4,
        )


def find_document_by_hash(file_hash):

    documents = load_documents()

    for document in documents:

        if document["file_hash"] == file_hash:

            return document

    return None


def add_document(document):

    documents = load_documents()

    documents.append(document)

    save_documents(documents)

def delete_document(document_id):

    documents = load_documents()

    remaining_documents = [
        document
        for document in documents
        if document["document_id"] != document_id
    ]

    save_documents(
        remaining_documents
    )

def find_document_by_id(document_id):

    documents = load_documents()

    for document in documents:

        if document["document_id"] == document_id:

            return document

    return None