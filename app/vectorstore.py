from langchain_chroma import Chroma

from embeddings import embeddings


VECTORSTORE_PATH = "vectorstore"


def create_vectorstore(pdf_path: str):

    from loaders import load_pdf
    from splitter import split_documents

    documents = load_pdf(pdf_path)

    chunks = split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH,
    )

    return vectorstore


def get_vectorstore():

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings,
    )

    return vectorstore

def delete_document_vectors(document_id: str):

    vectorstore = get_vectorstore()

    # Find all chunks belonging to this document
    results = vectorstore.get(
        where={
            "document_id": document_id
        }
    )

    ids = results.get("ids", [])

    if not ids:
        return 0

    # Delete those chunks
    vectorstore.delete(
        ids=ids
    )

    return len(ids)