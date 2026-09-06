from typing import List

from openai import OpenAI
from langchain_core.embeddings import Embeddings

from config import OPENROUTER_API_KEY


class OpenRouterEmbeddings(Embeddings):
    """
    Custom LangChain embedding wrapper for OpenRouter.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        self.model = "liquid/lfm-2.5-embedding-350m:free"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []

        for text in texts:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )

            embeddings.append(response.data[0].embedding)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding


embeddings = OpenRouterEmbeddings()