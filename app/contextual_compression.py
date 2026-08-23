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
            """You are a document relevance extraction system.

You will receive a user question and several document chunks.

For EACH document:

1. Extract ONLY information that is directly useful for
   answering the user's question.
2. Use ONLY information contained in that document.
3. Do NOT use outside knowledge.
4. Do NOT invent facts.
5. Preserve important:
   - definitions
   - explanations
   - examples
   - formulas
   - commands
   - numbers
   - conditions
6. Remove irrelevant information.
7. If a document does not contain useful information,
   return exactly:

NOT_RELEVANT

You MUST preserve the document numbering.

Return EXACTLY this structure:

DOCUMENT 1:
<relevant information or NOT_RELEVANT>

DOCUMENT 2:
<relevant information or NOT_RELEVANT>

DOCUMENT 3:
<relevant information or NOT_RELEVANT>

Continue for every document.

Do not add explanations before or after the results.
""",
        ),
        (
            "human",
            """USER QUESTION:

{question}

DOCUMENTS:

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
) -> List[Document]:

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

{document.page_content}"""
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
    # ONE LLM CALL
    # ========================================================

    response = llm.invoke(
        messages
    )


    compressed_text = (
        response.text.strip()
    )


    if not compressed_text:
        return []


    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    compressed_documents = []


    # Normalize line endings
    compressed_text = (
        compressed_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


    # --------------------------------------------------------
    # Split by DOCUMENT markers
    # --------------------------------------------------------

    sections = compressed_text.split(
        "DOCUMENT "
    )


    for section in sections:

        section = section.strip()

        if not section:
            continue


        lines = section.splitlines()

        if not lines:
            continue


        # ====================================================
        # EXTRACT DOCUMENT NUMBER
        # ====================================================

        first_line = lines[0].strip()


        try:

            number_text = (
                first_line
                .split(":", 1)[0]
                .strip()
            )

            document_number = int(
                number_text
            )

        except (
            ValueError,
            IndexError,
        ):

            continue


        # ====================================================
        # VALIDATE DOCUMENT NUMBER
        # ====================================================

        if not (
            1
            <= document_number
            <= len(documents)
        ):

            continue


        # ====================================================
        # EXTRACT COMPRESSED CONTENT
        # ====================================================

        content = "\n".join(
            lines[1:]
        ).strip()


        if not content:
            continue


        # ====================================================
        # IGNORE IRRELEVANT DOCUMENTS
        # ====================================================

        if content.upper() == "NOT_RELEVANT":
            continue


        # ====================================================
        # REMOVE ACCIDENTAL MARKERS
        # ====================================================

        if content.startswith(":"):

            content = content[1:].strip()


        if not content:
            continue


        # ====================================================
        # PRESERVE ORIGINAL METADATA
        # ====================================================

        original_document = documents[
            document_number - 1
        ]


        metadata = (
            original_document.metadata.copy()
        )


        metadata["compressed"] = True


        # ====================================================
        # CREATE COMPRESSED DOCUMENT
        # ====================================================

        compressed_document = Document(
            page_content=content,
            metadata=metadata,
        )


        compressed_documents.append(
            compressed_document
        )


    return compressed_documents