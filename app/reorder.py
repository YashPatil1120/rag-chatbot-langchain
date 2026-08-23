from typing import List

from langchain_core.documents import Document


def reorder_documents(
    documents: List[Document],
) -> List[Document]:

    if not documents:
        return []

    # --------------------------------------------------------
    # Short contexts do not need reordering
    # --------------------------------------------------------

    if len(documents) <= 2:
        return documents

    # --------------------------------------------------------
    # Take documents in relevance order
    # --------------------------------------------------------

    reordered = []

    left = 0
    right = len(documents) - 1

    # --------------------------------------------------------
    # Alternate strongest remaining documents between
    # beginning and end of context.
    # --------------------------------------------------------

    while left <= right:

        reordered.append(
            documents[left]
        )

        left += 1

        if left <= right:

            reordered.append(
                documents[right]
            )

            right -= 1

    return reordered