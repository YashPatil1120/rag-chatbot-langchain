import re
from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from llm import llm


# ============================================================
# CONTEXTUAL COMPRESSION PROMPT
# ============================================================

compression_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a document relevance extractor.

You are given a user question and multiple document chunks.

For EACH document:

- Extract only information directly useful for answering
  the user's question.
- Use ONLY information present in that document.
- Do not add outside knowledge.
- Do not invent facts.
- Preserve important definitions, explanations, examples,
  commands, numbers, formulas and conditions.
- Remove unrelated information.

If a document is not useful, write:

NOT_RELEVANT

You MUST use this exact structure:

DOCUMENT 1:
<content or NOT_RELEVANT>

DOCUMENT 2:
<content or NOT_RELEVANT>

DOCUMENT 3:
<content or NOT_RELEVANT>

Continue for every document.

Do not write explanations outside this structure.
""",
        ),
        (
            "human",
            """User question:

{question}

Documents:

{documents}
""",
        ),
    ]
)


# ============================================================
# COMPRESS DOCUMENTS
# ============================================================

def compress_documents(
    question: str,
    documents: List[Document],
):

    if not documents:
        return []


    # ========================================================
    # BUILD DOCUMENT INPUT
    # ========================================================

    document_blocks = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        document_blocks.append(
            f"""DOCUMENT {index}:

{document.page_content}
"""
        )

    combined_documents = "\n\n---\n\n".join(
        document_blocks
    )


    # ========================================================
    # CREATE PROMPT
    # ========================================================

    messages = compression_prompt.format_messages(
        question=question,
        documents=combined_documents,
    )


    # ========================================================
    # CALL LLM
    # ========================================================

    try:

        response = llm.invoke(
            messages
        )

    except Exception:

        # Compression should never break RAG.
        return []


    compressed_text = (
        response.content
        if hasattr(response, "content")
        else getattr(response, "text", "")
    )

    if not compressed_text:

        return []


    compressed_text = (
        str(compressed_text)
        .strip()
    )


    # ========================================================
    # PARSE DOCUMENT SECTIONS
    # ========================================================

    pattern = re.compile(
        r"DOCUMENT\s+(\d+)\s*:\s*(.*?)(?="
        r"\n\s*DOCUMENT\s+\d+\s*:|$)",
        re.IGNORECASE | re.DOTALL,
    )

    matches = pattern.findall(
        compressed_text
    )


    if not matches:

        return []


    compressed_documents = []


    # ========================================================
    # REBUILD DOCUMENTS
    # ========================================================

    for document_number_text, content in matches:

        try:

            document_number = int(
                document_number_text
            )

        except ValueError:

            continue


        if (
            document_number < 1
            or document_number > len(documents)
        ):

            continue


        content = content.strip()


        if not content:

            continue


        # ----------------------------------------------------
        # Ignore irrelevant documents
        # ----------------------------------------------------

        if (
            content.upper()
            .strip()
            == "NOT_RELEVANT"
        ):

            continue


        # ----------------------------------------------------
        # Preserve original metadata
        # ----------------------------------------------------

        original_document = documents[
            document_number - 1
        ]

        metadata = (
            original_document.metadata.copy()
        )

        metadata["compressed"] = True


        # ----------------------------------------------------
        # Create compressed document
        # ----------------------------------------------------

        compressed_document = Document(
            page_content=content,
            metadata=metadata,
        )

        compressed_documents.append(
            compressed_document
        )


    return compressed_documents