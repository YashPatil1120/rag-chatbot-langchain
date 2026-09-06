from langchain_core.prompts import ChatPromptTemplate

from llm import llm

from retriever import get_mmr_retriever

from reranker import (
    rerank_documents,
)

from contextual_compression import (
    compress_documents,
)

from reorder import (
    reorder_documents,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Contextual compression is an optimization layer.
# If it fails, the original reranked documents are retained.
USE_CONTEXTUAL_COMPRESSION = True


# MMR retrieval configuration
#
# MMR helps retrieve documents that are both:
# 1. Relevant to the question
# 2. Diverse from each other
#
# This also reduces the need for a separate
# redundancy-filtering API call.
MMR_K = 15
MMR_FETCH_K = 30
MMR_LAMBDA = 0.5


# Number of documents retained after Cohere reranking
RERANK_TOP_N = 5


# ============================================================
# QUESTION REWRITING PROMPT
# ============================================================

rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a question rewriting assistant.

Convert the user's latest question into a standalone
question that can be understood without the previous
conversation.

Use the conversation history only when necessary.

If the question is already standalone, return it unchanged.

Return ONLY the rewritten question.
Do not explain anything.
""",
        ),
        (
            "human",
            """Conversation history:

{chat_history}

Latest question:

{question}
""",
        ),
    ]
)


# ============================================================
# FINAL RAG PROMPT
# ============================================================

rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful document question-answering
assistant.

Answer the user's question using ONLY the provided
document context.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. If the answer cannot be found in the context,
   say exactly:

"I don't know based on the provided document."

4. Keep the answer clear and concise.
5. If multiple documents contain relevant information,
   combine them carefully.
6. Preserve important technical details, formulas,
   commands, numbers, and definitions.

Context:

{context}
""",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(
    question: str,
    chat_history=None,
    document_id=None,
):

    # ========================================================
    # 1. NORMALIZE INPUT
    # ========================================================

    if chat_history is None:
        chat_history = []

    question = question.strip()

    if not question:
        return (
            None,
            [],
            "",
        )


    # ========================================================
    # 2. BUILD CHAT HISTORY TEXT
    # ========================================================

    history_text = ""

    for message in chat_history:

        role = message.get(
            "role",
            "",
        )

        content = message.get(
            "content",
            "",
        )

        if content:

            history_text += (
                f"{role}: {content}\n"
            )


    # ========================================================
    # 3. QUESTION REWRITING
    # ========================================================

    if chat_history:

        rewrite_messages = (
            rewrite_prompt.format_messages(
                chat_history=history_text,
                question=question,
            )
        )

        try:

            rewritten_response = llm.invoke(
                rewrite_messages
            )

            # ChatOpenAI / OpenRouter normally returns
            # response.content.
            standalone_question = (
                getattr(
                    rewritten_response,
                    "content",
                    "",
                )
                or getattr(
                    rewritten_response,
                    "text",
                    "",
                )
            ).strip()

        except Exception:

            # If rewriting fails, the original question
            # should still be used for retrieval.
            standalone_question = question


        if not standalone_question:

            standalone_question = question

    else:

        standalone_question = question


    # ========================================================
    # 4. MMR RETRIEVAL
    # ========================================================

    retriever = get_mmr_retriever(
        k=MMR_K,
        fetch_k=MMR_FETCH_K,
        lambda_mult=MMR_LAMBDA,
        document_id=document_id,
    )

    documents = retriever.invoke(
        standalone_question
    )


    # ========================================================
    # 5. NO DOCUMENTS FOUND
    # ========================================================

    if not documents:

        return (
            None,
            [],
            standalone_question,
        )


    # ========================================================
    # 6. COHERE RERANKING
    # ========================================================

    documents = rerank_documents(
        question=standalone_question,
        documents=documents,
        top_n=RERANK_TOP_N,
    )


    # ========================================================
    # 7. NO DOCUMENTS AFTER RERANKING
    # ========================================================

    if not documents:

        return (
            None,
            [],
            standalone_question,
        )


    # ========================================================
    # 8. SAVE SUCCESSFULLY RETRIEVED DOCUMENTS
    # ========================================================

    # These documents are our reliable fallback.
    #
    # Contextual compression is optional.
    # If compression fails, these original reranked
    # documents will be used.
    retrieved_documents = documents


    # ========================================================
    # 9. CONTEXTUAL COMPRESSION
    # ========================================================

    if USE_CONTEXTUAL_COMPRESSION:

        try:

            compressed_documents = (
                compress_documents(
                    question=standalone_question,
                    documents=retrieved_documents,
                )
            )

        except Exception:

            # Compression is an optimization layer.
            # If it fails, continue with original documents.
            compressed_documents = []


        # ====================================================
        # 10. COMPRESSION FALLBACK
        # ====================================================

        # IMPORTANT:
        #
        # Never return "I don't know" merely because the
        # compression model failed to format its response.
        #
        # Use the original reranked documents instead.

        if compressed_documents:

            documents = compressed_documents

        else:

            documents = retrieved_documents

    else:

        documents = retrieved_documents


    # ========================================================
    # 11. FINAL SAFETY CHECK
    # ========================================================

    if not documents:

        # This should almost never happen because of the
        # fallback above, but protects the final pipeline.
        return (
            None,
            [],
            standalone_question,
        )


    # ========================================================
    # 12. LONG-CONTEXT REORDERING
    # ========================================================

    documents = reorder_documents(
        documents
    )


    # ========================================================
    # 13. FINAL SAFETY CHECK AFTER REORDERING
    # ========================================================

    if not documents:

        documents = retrieved_documents


    # ========================================================
    # 14. BUILD FINAL CONTEXT
    # ========================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        content = (
            document.page_content
            if document.page_content
            else ""
        )

        if not content.strip():
            continue

        context_parts.append(
            f"""Document {index}:

{content}"""
        )


    # ========================================================
    # 15. NO USABLE CONTEXT
    # ========================================================

    if not context_parts:

        return (
            None,
            [],
            standalone_question,
        )


    context = "\n\n---\n\n".join(
        context_parts
    )


    # ========================================================
    # 16. CREATE FINAL RAG PROMPT
    # ========================================================

    messages = rag_prompt.format_messages(
        context=context,
        question=standalone_question,
    )


    # ========================================================
    # 17. FINAL LLM ANSWER
    # ========================================================

    try:

        response = llm.invoke(
            messages
        )

    except Exception:

        # Let the UI handle a failed final LLM request
        # without pretending retrieval failed.
        raise


    # ========================================================
    # 18. RETURN
    # ========================================================

    return (
        response,
        documents,
        standalone_question,
    )