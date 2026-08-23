from retriever import get_retriever


retriever = get_retriever(k=5)


questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
    "What is the capital of France?",
]


for question in questions:

    print("\n")
    print("=" * 60)
    print("QUESTION:", question)
    print("=" * 60)

    documents = retriever.invoke(question)

    print("Retrieved documents:", len(documents))

    for i, document in enumerate(documents, start=1):

        print(f"\n--- RESULT {i} ---")
        print("Page:", document.metadata.get("page"))
        print("Content:")
        print(document.page_content[:500])