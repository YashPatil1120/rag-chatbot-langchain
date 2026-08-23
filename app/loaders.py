from pathlib import Path

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    Docx2txtLoader,
)


def load_document(file_path: str):
    """
    Load a PDF, TXT, or DOCX document.

    Returns:
        List of LangChain Document objects.
    """

    extension = Path(file_path).suffix.lower()

    # ---------------------------------
    # PDF
    # ---------------------------------

    if extension == ".pdf":

        loader = PyMuPDFLoader(file_path)

    # ---------------------------------
    # TXT
    # ---------------------------------

    elif extension == ".txt":

        loader = TextLoader(
            file_path,
            encoding="utf-8",
        )

    # ---------------------------------
    # DOCX
    # ---------------------------------

    elif extension == ".docx":

        loader = Docx2txtLoader(file_path)

    # ---------------------------------
    # Unsupported file
    # ---------------------------------

    else:

        raise ValueError(
            f"Unsupported file type: {extension}. "
            "Only PDF, TXT, and DOCX files are supported."
        )

    documents = loader.load()

    # ---------------------------------
    # Remove empty documents
    # ---------------------------------

    documents = [
        document
        for document in documents
        if document.page_content.strip()
    ]

    return documents