from llm import llm

response = llm.invoke("Explain RAG in one simple paragraph.")

print(response.text)