
from langchain_openai import ChatOpenAI

from config import OPENROUTER_API_KEY


llm = ChatOpenAI(
    model="openrouter/free",

    api_key=OPENROUTER_API_KEY,

    base_url="https://openrouter.ai/api/v1",

    temperature=0,
)