import os

import streamlit as st
from dotenv import load_dotenv


# ============================================================
# LOAD LOCAL .ENV
# ============================================================

load_dotenv()


# ============================================================
# HELPER
# ============================================================

def get_secret(key: str):
    """
    Get a secret from Streamlit Cloud Secrets first.
    Fall back to the local .env environment variable.
    """

    try:
        value = st.secrets.get(key)
    except Exception:
        value = None

    if value:
        return value

    return os.getenv(key)


# ============================================================
# GOOGLE
# ============================================================

GOOGLE_API_KEY = get_secret(
    "GOOGLE_API_KEY"
)


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = get_secret(
    "OPENROUTER_API_KEY"
)


# ============================================================
# COHERE
# ============================================================

COHERE_API_KEY = get_secret(
    "COHERE_API_KEY"
)