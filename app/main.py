import os
import html
from pathlib import Path

import streamlit as st

from ingest import (
    ingest_document,
    calculate_file_hash,
)

from document_store import (
    find_document_by_hash,
    load_documents,
)

from document_manager import remove_document

from rag import ask_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

UPLOAD_DIRECTORY = Path("data/uploads")

SUPPORTED_FILE_TYPES = [
    "pdf",
    "txt",
    "docx",
]

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}

QUESTION_COLOR = "#ef4444"
ANSWER_COLOR = "#f59e0b"


# ============================================================
# SESSION STATE
# ============================================================

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "last_ingestion" not in st.session_state:
    st.session_state.last_ingestion = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_file_path(file_name: str):
    """
    Find the locally stored document.
    """

    upload_path = UPLOAD_DIRECTORY / file_name
    original_path = Path("data") / file_name

    if upload_path.exists():
        return str(upload_path)

    if original_path.exists():
        return str(original_path)

    return None


def get_source_filename(document):
    """
    Safely extract the original filename from metadata.
    """

    metadata = document.metadata or {}

    file_name = metadata.get("file_name")

    if file_name:
        return os.path.basename(str(file_name))

    source = metadata.get("source")

    if source:
        return os.path.basename(str(source))

    file_path = metadata.get("file_path")

    if file_path:
        return os.path.basename(str(file_path))

    return "Unknown document"


def get_page_number(document):
    """
    Extract page number from document metadata.

    Existing pipeline uses page + 1 for display.
    """

    metadata = document.metadata or {}

    page = metadata.get("page")

    if page is None:
        return None

    try:
        page = int(page)
    except (TypeError, ValueError):
        return None

    return page + 1


def build_sources(documents):
    """
    Build a compact source list from retrieved documents.
    """

    sources = {}

    for document in documents:

        file_name = get_source_filename(document)
        page_number = get_page_number(document)

        if file_name not in sources:
            sources[file_name] = set()

        if page_number is not None:
            sources[file_name].add(page_number)

    result = []

    for file_name, pages in sources.items():

        result.append(
            {
                "file_name": file_name,
                "pages": sorted(pages),
            }
        )

    return result


def save_chat_message(
    session_key,
    role,
    content,
    documents=None,
    sources=None,
    standalone_question=None,
):
    """
    Save a chat message.

    Retrieval information is stored with assistant messages
    so evidence remains available when the chat is displayed.
    """

    if session_key not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[session_key] = []

    message = {
        "role": role,
        "content": content,
    }

    if documents is not None:
        message["documents"] = documents

    if sources is not None:
        message["sources"] = sources

    if standalone_question is not None:
        message["standalone_question"] = standalone_question

    st.session_state.chat_sessions[session_key].append(
        message
    )


def ingest_uploaded_file(uploaded_file):
    """
    Save and ingest a Streamlit UploadedFile.

    Supports:
        PDF
        TXT
        DOCX
    """

    if uploaded_file is None:
        return None

    file_extension = Path(
        uploaded_file.name
    ).suffix.lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. "
            "Only PDF, TXT, and DOCX files are supported."
        )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = UPLOAD_DIRECTORY / uploaded_file.name

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    with open(
        file_path,
        "wb",
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    # --------------------------------------------------------
    # Calculate file hash
    # --------------------------------------------------------

    file_hash = calculate_file_hash(
        str(file_path)
    )

    # --------------------------------------------------------
    # Duplicate check
    # --------------------------------------------------------

    existing_document = (
        find_document_by_hash(
            file_hash
        )
    )

    if existing_document:

        return {
            **existing_document,
            "already_exists": True,
        }

    # --------------------------------------------------------
    # Ingest
    # --------------------------------------------------------

    result = ingest_document(
        file_path=str(file_path),
        original_filename=uploaded_file.name,
    )

    return result


def show_upload_result(result):
    """
    Display a compact upload result.
    """

    if not result:
        return

    if result.get("already_exists", False):

        st.warning(
            f"{result.get('file_name', 'Document')} "
            "is already indexed."
        )

        return

    st.success(
        f"{result.get('file_name', 'Document')} "
        "indexed successfully."
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html,
    body {{
        background: #ffffff !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background: #ffffff !important;
    }}

    [data-testid="stHeader"] {{
        background: #ffffff !important;
    }}

    [data-testid="stToolbar"] {{
        background: #ffffff !important;
    }}

    .block-container {{
        padding-top: 0.15rem !important;
        padding-bottom: 1rem !important;
    }}


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {{
        background: #f3f3f3 !important;
        border-right: 1px solid #e5e5e5;
    }}

    [data-testid="stSidebarContent"] {{
        padding-top: 0.25rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        padding-bottom: 1rem !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #222222 !important;
    }}


    /* ======================================================
       SIDEBAR BRAND
       ====================================================== */

    .sidebar-brand {{
        font-size: 1.5rem;
        font-weight: 700;
        color: #222222;
        margin-top: 0;
        margin-bottom: 1.25rem;
        line-height: 1.2;
    }}


    /* ======================================================
       SIDEBAR TYPOGRAPHY
       ====================================================== */

    .sidebar-section-title {{
        font-size: 1.02rem;
        font-weight: 650;
        color: #333333;
        margin-top: 0.75rem;
        margin-bottom: 0.55rem;
        line-height: 1.3;
    }}

    .sidebar-label {{
        font-size: 0.9rem;
        color: #777777;
        margin-bottom: 0.2rem;
    }}

    .knowledge-count {{
        font-size: 0.88rem;
        color: #555555;
        line-height: 1.6;
    }}

    .indexed-document-name {{
        font-size: 0.9rem;
        color: #333333;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.35;
    }}

    .document-meta {{
        font-size: 0.78rem;
        color: #888888;
        margin-left: 2px;
        margin-bottom: 7px;
        line-height: 1.25;
    }}


    /* ======================================================
       SIDEBAR CONTROLS
       ====================================================== */

    [data-testid="stSidebar"] button {{
        min-width: 34px !important;
        min-height: 34px !important;
        border-radius: 7px !important;

        transition:
            background-color 0.12s ease,
            border-color 0.12s ease;
    }}

    [data-testid="stSidebar"] button svg {{
        width: 18px !important;
        height: 18px !important;
    }}

    [data-testid="stSidebar"] button:hover {{
        background: #dddddd !important;
        border-color: #cfcfcf !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] {{
        min-height: 40px !important;
        border-radius: 8px !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] * {{
        font-size: 0.9rem !important;
    }}


    /* ======================================================
       INDEXED DOCUMENT ROW
       ====================================================== */

    .indexed-document {{
        display: flex;
        align-items: center;
        min-height: 36px;
        margin-bottom: 3px;
        padding: 5px 7px;
        border-radius: 7px;
        transition: background-color 0.12s ease;
    }}

    .indexed-document:hover {{
        background: #dddddd;
    }}


    /* ======================================================
       SIDEBAR DIVIDER
       ====================================================== */

    [data-testid="stSidebar"] hr {{
        border-color: #d3d3d3 !important;
        margin-top: 1.1rem !important;
        margin-bottom: 1.1rem !important;
    }}


    /* ======================================================
       MAIN CONTENT
       ====================================================== */

    .main-wrapper {{
        max-width: 1050px;
        margin: 0 auto;
        padding: 0.05rem 2rem 6rem 2rem;
    }}

    .main-title {{
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #222222;
        margin-top: 0;
        margin-bottom: 0.25rem;
        line-height: 1.25;
    }}

    .main-subtitle {{
        text-align: center;
        color: #777777;
        font-size: 0.92rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }}


    /* ======================================================
       EMPTY STATE
       ====================================================== */

    .empty-state {{
        text-align: center;
        color: #888888;
        font-size: 0.92rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}


    /* ======================================================
       CHAT MESSAGE AREA
       ====================================================== */

    .qa-block {{
        margin-top: 1.15rem;
        margin-bottom: 1.35rem;
    }}

    .qa-row {{
        display: flex;
        align-items: flex-start;
        gap: 11px;
    }}

    .qa-icon {{
        min-width: 27px;
        width: 27px;
        height: 27px;
        border-radius: 7px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 0.78rem;
        font-weight: 700;

        margin-top: 2px;
    }}

    .question-icon {{
        background: {QUESTION_COLOR};
        color: #ffffff;
    }}

    .answer-icon {{
        background: {ANSWER_COLOR};
        color: #ffffff;
    }}

    .question-text {{
        color: #222222;
        font-size: 1rem;
        line-height: 1.55;
        font-weight: 500;
        padding-top: 1px;
    }}

    .answer-label {{
        color: #555555;
        font-size: 0.82rem;
        font-weight: 650;
        margin-bottom: 3px;
    }}

    .answer-content {{
        color: #222222;
        font-size: 0.98rem;
        line-height: 1.65;
    }}


    /* ======================================================
       EVIDENCE
       ====================================================== */

    .evidence-divider {{
        height: 1px;
        background: #eeeeee;
        margin: 1rem 0 0.75rem 0;
    }}

    .evidence-text {{
        font-size: 0.82rem;
        line-height: 1.5;
        color: #666666;
    }}

    .evidence-document-title {{
        font-size: 0.86rem;
        font-weight: 600;
        color: #444444;
    }}


    /* ======================================================
       EXPANDERS
       ====================================================== */

    [data-testid="stExpander"] {{
        border: 1px solid #d9d9d9 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        box-shadow: none !important;
        transition:
            border-color 0.12s ease,
            background-color 0.12s ease;
    }}

    [data-testid="stExpander"]:hover {{
        border-color: #c8c8c8 !important;
        background: #fafafa !important;
    }}

    [data-testid="stExpander"] summary {{
        font-size: 0.82rem !important;
        color: #555555 !important;
        min-height: 34px !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        background: #f3f3f3 !important;
    }}


    /* ======================================================
       CHAT INPUT
       ====================================================== */

    [data-testid="stChatInput"] {{
        background: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] > div {{
        background: #f2f2f2 !important;
        border: 1px solid #dcdcdc !important;
        border-radius: 9px !important;

        box-shadow: none !important;

        transition:
            border-color 0.12s ease,
            background-color 0.12s ease;
    }}

    [data-testid="stChatInput"] > div:focus-within {{
        border-color: {QUESTION_COLOR} !important;
        background: #f7f7f7 !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: #333333 !important;
        font-size: 0.92rem !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: #888888 !important;
    }}

    [data-testid="stChatInput"] button {{
        border-radius: 7px !important;

        transition:
            background-color 0.12s ease,
            border-color 0.12s ease;
    }}

    [data-testid="stChatInput"] button:hover {{
        background: #dddddd !important;
    }}


    /* ======================================================
       GENERAL BUTTON HOVER
       ====================================================== */

    button {{
        transition:
            background-color 0.12s ease,
            border-color 0.12s ease;
    }}

    button:hover {{
        background: #eeeeee !important;
    }}


    /* ======================================================
       POPOVER
       ====================================================== */

    [data-testid="stPopover"] button:hover {{
        background: #dddddd !important;
    }}


    /* ======================================================
       REMOVE UNNECESSARY STREAMLIT SPACING
       ====================================================== */

    [data-testid="stVerticalBlock"] {{
        gap: 0.45rem;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DOCUMENTS
# ============================================================

documents = load_documents()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # BRAND
    # ========================================================

    st.markdown(
        '<div class="sidebar-brand">RAG Chatbot</div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # DOCUMENT MANAGER
    # ========================================================

    st.markdown(
        '<div class="sidebar-section-title">'
        'Document Manager'
        '</div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # KNOWLEDGE BASE
    # ========================================================

    st.markdown(
        '<div class="sidebar-section-title">'
        'Knowledge Base'
        '</div>',
        unsafe_allow_html=True,
    )

    total_documents = len(documents)

    total_chunks = sum(
        document.get("chunks", 0)
        for document in documents
    )

    kb_col1, kb_col2 = st.columns(
        [5, 1],
        vertical_alignment="center",
    )

    with kb_col1:

        st.markdown(
            f"""
            <div class="knowledge-count">
                {total_documents} documents
                <br>
                {total_chunks} chunks
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kb_col2:

        with st.popover(
            "",
            icon=":material/add:",
            help="Add a document",
        ):

            st.markdown(
                "**Add to Knowledge Base**"
            )

            sidebar_upload = st.file_uploader(
                "Upload document",
                type=SUPPORTED_FILE_TYPES,
                accept_multiple_files=False,
                label_visibility="collapsed",
                help="PDF, DOCX or TXT",
                key="sidebar_uploader",
            )

            if sidebar_upload is not None:

                if st.button(
                    "Add Document",
                    use_container_width=True,
                    key="sidebar_add_document",
                ):

                    try:

                        with st.spinner(
                            "Indexing document..."
                        ):

                            result = ingest_uploaded_file(
                                sidebar_upload
                            )

                        show_upload_result(
                            result
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "Document ingestion failed."
                        )

                        st.exception(error)


    # ========================================================
    # SEARCH SCOPE
    # ========================================================

    st.markdown(
        '<div class="sidebar-section-title">'
        'Search Scope'
        '</div>',
        unsafe_allow_html=True,
    )

    document_options = {
        "All Documents": None,
    }

    for document in documents:

        document_options[
            document["file_name"]
        ] = document["document_id"]

    selected_document_name = st.selectbox(
        "Search in",
        options=list(document_options.keys()),
        label_visibility="collapsed",
        key="search_scope",
    )

    selected_document_id = document_options[
        selected_document_name
    ]


    # ========================================================
    # CHAT
    # ========================================================

    st.markdown(
        '<div class="sidebar-section-title">'
        'Chat'
        '</div>',
        unsafe_allow_html=True,
    )

    if selected_document_id:

        chat_session_key = selected_document_id

    else:

        chat_session_key = "all_documents"

    if chat_session_key not in st.session_state.chat_sessions:

        st.session_state.chat_sessions[
            chat_session_key
        ] = []

    chat_col1, chat_col2 = st.columns(
        [5, 1],
        vertical_alignment="center",
    )

    with chat_col1:

        st.markdown(
            f"""
            <div class="sidebar-label">
                {html.escape(selected_document_name)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with chat_col2:

        if st.button(
            "",
            icon=":material/delete_sweep:",
            help="Clear current chat",
            key=f"clear_chat_{chat_session_key}",
        ):

            st.session_state.chat_sessions[
                chat_session_key
            ] = []

            st.rerun()


    # ========================================================
    # DIVIDER
    # ========================================================

    st.divider()


    # ========================================================
    # INDEXED DOCUMENTS
    # ========================================================

    st.markdown(
        '<div class="sidebar-section-title">'
        'Indexed Documents'
        '</div>',
        unsafe_allow_html=True,
    )

    if not documents:

        st.markdown(
            """
            <div class="sidebar-label">
                No documents indexed.
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        for document in documents:

            file_name = document["file_name"]
            document_id = document["document_id"]

            doc_col1, doc_col2 = st.columns(
                [6, 1],
                vertical_alignment="center",
            )

            with doc_col1:

                st.markdown(
                    f"""
                    <div class="indexed-document">
                        <div>
                            <div class="indexed-document-name">
                                {html.escape(file_name)}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="document-meta">
                        {document.get("pages", 0)} pages
                        &nbsp;•&nbsp;
                        {document.get("chunks", 0)} chunks
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with doc_col2:

                if st.button(
                    "",
                    icon=":material/delete:",
                    help=f"Delete {file_name}",
                    key=f"delete_{document_id}",
                ):

                    file_path = get_file_path(
                        file_name
                    )

                    try:

                        with st.spinner(
                            "Deleting..."
                        ):

                            remove_document(
                                document_id=document_id,
                                file_path=file_path,
                            )

                        if (
                            document_id
                            in st.session_state.chat_sessions
                        ):

                            del st.session_state.chat_sessions[
                                document_id
                            ]

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "Unable to delete document."
                        )

                        st.exception(error)


# ============================================================
# MAIN CONTENT WRAPPER
# ============================================================

st.markdown(
    '<div class="main-wrapper">',
    unsafe_allow_html=True,
)


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">RAG Document Chatbot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-subtitle">'
    'Ask questions about your indexed documents.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# CURRENT CHAT HISTORY
# ============================================================

current_messages = (
    st.session_state.chat_sessions[
        chat_session_key
    ]
)


# ============================================================
# EMPTY STATE
# ============================================================

if not current_messages:

    if not documents:

        st.markdown(
            """
            <div class="empty-state">
                Add a document to start asking questions.
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="empty-state">
                Ask a question about your documents.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in current_messages:

    role = message.get("role")
    content = message.get("content", "")


    # ========================================================
    # USER QUESTION
    # ========================================================

    if role == "user":

        st.markdown(
            f"""
            <div class="qa-block">
                <div class="qa-row">

                    <div class="qa-icon question-icon">
                        ?
                    </div>

                    <div class="question-text">
                        {html.escape(content)}
                    </div>

                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ========================================================
    # ASSISTANT ANSWER
    # ========================================================

    else:

        st.markdown(
            """
            <div class="qa-block">
                <div class="qa-row">

                    <div class="qa-icon answer-icon">
                        A
                    </div>

                    <div style="flex:1;">

                        <div class="answer-label">
                            Answer
                        </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            content
        )

        st.markdown(
            """
                    </div>

                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # EVIDENCE
        # ====================================================

        message_documents = message.get(
            "documents",
            [],
        )

        message_sources = message.get(
            "sources",
            [],
        )

        if message_documents or message_sources:

            st.markdown(
                '<div class="evidence-divider"></div>',
                unsafe_allow_html=True,
            )

            evidence_col1, evidence_col2 = st.columns(
                2,
                gap="small",
            )


            # =================================================
            # RETRIEVED DOCUMENTS
            # =================================================

            with evidence_col1:

                with st.expander(
                    f"Retrieved Documents "
                    f"({len(message_documents)})",
                    expanded=False,
                ):

                    if message_documents:

                        for index, document in enumerate(
                            message_documents,
                            start=1,
                        ):

                            file_name = get_source_filename(
                                document
                            )

                            page = get_page_number(
                                document
                            )

                            st.markdown(
                                f"""
                                <div class="evidence-text">
                                    <span class="evidence-document-title">
                                        Document {index}
                                    </span>
                                    <br>
                                    {html.escape(file_name)}
                                    {
                                        f" · Page {page}"
                                        if page is not None
                                        else ""
                                    }
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown(
                                "---"
                            )

                            # ---------------------------------
                            # Actual retrieved content appears
                            # ONLY after expander is opened.
                            # ---------------------------------

                            st.markdown(
                                document.page_content
                            )

                    else:

                        st.caption(
                            "No retrieved documents."
                        )


            # =================================================
            # SOURCES
            # =================================================

            with evidence_col2:

                with st.expander(
                    f"Sources ({len(message_sources)})",
                    expanded=False,
                ):

                    if message_sources:

                        for source in message_sources:

                            file_name = source[
                                "file_name"
                            ]

                            pages = source[
                                "pages"
                            ]

                            if pages:

                                pages_text = ", ".join(
                                    str(page)
                                    for page in pages
                                )

                                st.markdown(
                                    f"""
                                    <div class="evidence-text">
                                        <span class="evidence-document-title">
                                            {html.escape(file_name)}
                                        </span>
                                        <br>
                                        Page(s): {pages_text}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            else:

                                st.markdown(
                                    f"""
                                    <div class="evidence-text">
                                        <span class="evidence-document-title">
                                            {html.escape(file_name)}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            st.markdown(
                                "---"
                            )

                    else:

                        st.caption(
                            "No sources available."
                        )


# ============================================================
# CHAT INPUT
# ============================================================

chat_input = st.chat_input(
    "Ask a question about your documents...",
    accept_file=True,
    file_type=SUPPORTED_FILE_TYPES,
)


# ============================================================
# PROCESS CHAT INPUT
# ============================================================

if chat_input is not None:

    # ========================================================
    # EXTRACT QUESTION
    # ========================================================

    if hasattr(
        chat_input,
        "text",
    ):

        question = chat_input.text.strip()

    else:

        question = str(
            chat_input
        ).strip()


    # ========================================================
    # EXTRACT ATTACHED FILES
    # ========================================================

    attached_files = []

    if hasattr(
        chat_input,
        "files",
    ):

        attached_files = chat_input.files


    # ========================================================
    # PROCESS FILES ATTACHED THROUGH CHAT INPUT
    # ========================================================

    if attached_files:

        for uploaded_file in attached_files:

            try:

                with st.spinner(
                    f"Indexing {uploaded_file.name}..."
                ):

                    result = ingest_uploaded_file(
                        uploaded_file
                    )

                if result.get(
                    "already_exists",
                    False,
                ):

                    st.toast(
                        f"{uploaded_file.name} "
                        "is already indexed."
                    )

                else:

                    st.toast(
                        f"{uploaded_file.name} "
                        "indexed successfully."
                    )

            except Exception as error:

                st.error(
                    f"Could not index "
                    f"{uploaded_file.name}."
                )

                st.exception(error)


        # ----------------------------------------------------
        # Reload document registry
        # ----------------------------------------------------

        documents = load_documents()


    # ========================================================
    # NO QUESTION
    # ========================================================

    if not question:

        if attached_files:
            st.rerun()


    else:

        # ====================================================
        # SAVE OLD HISTORY
        # ====================================================

        chat_history = (
            st.session_state.chat_sessions[
                chat_session_key
            ].copy()
        )


        # ====================================================
        # DISPLAY QUESTION IMMEDIATELY
        # ====================================================

        st.markdown(
            f"""
            <div class="qa-block">
                <div class="qa-row">

                    <div class="qa-icon question-icon">
                        ?
                    </div>

                    <div class="question-text">
                        {html.escape(question)}
                    </div>

                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        with st.spinner(
            "Searching documents..."
        ):

            try:

                (
                    response,
                    retrieved_documents,
                    standalone_question,
                ) = ask_question(
                    question=question,
                    chat_history=chat_history,
                    document_id=selected_document_id,
                )

            except Exception as error:

                st.error(
                    "An error occurred while processing "
                    "your question."
                )

                st.exception(error)

                response = None
                retrieved_documents = []
                standalone_question = question


        # ====================================================
        # FINAL ANSWER
        # ====================================================

        if response is None:

            answer = (
                "I don't know based on "
                "the provided documents."
            )

        else:

            answer = response.text.strip()


        # ====================================================
        # DISPLAY ANSWER
        # ====================================================

        st.markdown(
            """
            <div class="qa-block">
                <div class="qa-row">

                    <div class="qa-icon answer-icon">
                        A
                    </div>

                    <div style="flex:1;">

                        <div class="answer-label">
                            Answer
                        </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            answer
        )

        st.markdown(
            """
                    </div>

                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # BUILD SOURCES
        # ====================================================

        sources = build_sources(
            retrieved_documents
        )


        # ====================================================
        # EVIDENCE SECTION
        # ====================================================

        if retrieved_documents or sources:

            st.markdown(
                '<div class="evidence-divider"></div>',
                unsafe_allow_html=True,
            )

            evidence_col1, evidence_col2 = st.columns(
                2,
                gap="small",
            )


            # =================================================
            # RETRIEVED DOCUMENTS
            # =================================================

            with evidence_col1:

                with st.expander(
                    f"Retrieved Documents "
                    f"({len(retrieved_documents)})",
                    expanded=False,
                ):

                    if retrieved_documents:

                        for index, document in enumerate(
                            retrieved_documents,
                            start=1,
                        ):

                            file_name = (
                                get_source_filename(
                                    document
                                )
                            )

                            page = get_page_number(
                                document
                            )

                            st.markdown(
                                f"""
                                <div class="evidence-text">
                                    <span class="evidence-document-title">
                                        Document {index}
                                    </span>
                                    <br>
                                    {html.escape(file_name)}
                                    {
                                        f" · Page {page}"
                                        if page is not None
                                        else ""
                                    }
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown("---")

                            # Actual content is hidden until
                            # the user opens the expander.

                            st.markdown(
                                document.page_content
                            )

                    else:

                        st.caption(
                            "No retrieved documents."
                        )


            # =================================================
            # SOURCES
            # =================================================

            with evidence_col2:

                with st.expander(
                    f"Sources ({len(sources)})",
                    expanded=False,
                ):

                    if sources:

                        for source in sources:

                            file_name = source[
                                "file_name"
                            ]

                            pages = source[
                                "pages"
                            ]

                            if pages:

                                pages_text = ", ".join(
                                    str(page)
                                    for page in pages
                                )

                                st.markdown(
                                    f"""
                                    <div class="evidence-text">
                                        <span class="evidence-document-title">
                                            {html.escape(file_name)}
                                        </span>
                                        <br>
                                        Page(s): {pages_text}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            else:

                                st.markdown(
                                    f"""
                                    <div class="evidence-text">
                                        <span class="evidence-document-title">
                                            {html.escape(file_name)}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            st.markdown("---")

                    else:

                        st.caption(
                            "No sources available."
                        )


        # ====================================================
        # SAVE QUESTION
        # ====================================================

        save_chat_message(
            session_key=chat_session_key,
            role="user",
            content=question,
        )


        # ====================================================
        # SAVE ANSWER + EVIDENCE
        # ====================================================

        save_chat_message(
            session_key=chat_session_key,
            role="assistant",
            content=answer,
            documents=retrieved_documents,
            sources=sources,
            standalone_question=standalone_question,
        )


# ============================================================
# CLOSE MAIN WRAPPER
# ============================================================

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)