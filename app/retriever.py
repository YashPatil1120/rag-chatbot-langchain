from langchain_chroma import Chroma

from embeddings import embeddings


VECTORSTORE_PATH = "vectorstore"


# ============================================================
# VECTORSTORE
# ============================================================

def get_vectorstore():

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings,
    )

    return vectorstore


# ============================================================
# SIMILARITY RETRIEVER
# ============================================================

def get_similarity_retriever(
    k: int = 5,
    document_id=None,
):

    vectorstore = get_vectorstore()

    search_kwargs = {
        "score_threshold": 0.45,
        "k": k,
    }

    # ---------------------------------
    # Document filtering
    # ---------------------------------

    if document_id:

        search_kwargs["filter"] = {
            "document_id": document_id
        }

    retriever = vectorstore.as_retriever(

        search_type="similarity_score_threshold",

        search_kwargs=search_kwargs,

    )

    return retriever


# ============================================================
# MMR RETRIEVER
# ============================================================

def get_mmr_retriever(
    k: int = 5,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
    document_id=None,
):

    vectorstore = get_vectorstore()

    search_kwargs = {

        "k": k,

        "fetch_k": fetch_k,

        "lambda_mult": lambda_mult,

    }

    # ---------------------------------
    # Document filtering
    # ---------------------------------

    if document_id:

        search_kwargs["filter"] = {
            "document_id": document_id
        }

    retriever = vectorstore.as_retriever(

        search_type="mmr",

        search_kwargs=search_kwargs,

    )

    return retriever