from typing import List

from langchain_core.documents import Document

from embeddings import embeddings


# ============================================================
# REDUNDANT DOCUMENT FILTER
# ============================================================

def remove_redundant_documents(
    documents: List[Document],
    similarity_threshold: float = 0.90,
):
    """
    Remove highly similar/redundant document chunks.

    The original Document objects are preserved, including
    their metadata.
    """

    if not documents:
        return []

    selected_documents = []
    selected_embeddings = []

    for document in documents:

        current_text = document.page_content.strip()

        if not current_text:
            continue

        # ----------------------------------------------------
        # Create embedding for current document
        # ----------------------------------------------------

        current_embedding = embeddings.embed_query(
            current_text
        )

        # ----------------------------------------------------
        # First document is always accepted
        # ----------------------------------------------------

        if not selected_documents:

            selected_documents.append(
                document
            )

            selected_embeddings.append(
                current_embedding
            )

            continue

        # ----------------------------------------------------
        # Compare with already selected documents
        # ----------------------------------------------------

        is_redundant = False

        for selected_embedding in selected_embeddings:

            similarity = _cosine_similarity(
                current_embedding,
                selected_embedding,
            )

            if similarity >= similarity_threshold:

                is_redundant = True
                break

        # ----------------------------------------------------
        # Keep non-redundant document
        # ----------------------------------------------------

        if not is_redundant:

            selected_documents.append(
                document
            )

            selected_embeddings.append(
                current_embedding
            )

    return selected_documents


# ============================================================
# COSINE SIMILARITY
# ============================================================

def _cosine_similarity(
    vector_a,
    vector_b,
):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):

        return 0.0

    return (
        dot_product
        / (
            magnitude_a
            * magnitude_b
        )
    )