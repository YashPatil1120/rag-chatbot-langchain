from retriever import get_vectorstore


vectorstore = get_vectorstore()


questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
    "What is the capital of France?",
]


for question in questions:

    print("\n")
    print("=" * 70)
    print("QUESTION:", question)
    print("=" * 70)

    results = vectorstore.similarity_search_with_relevance_scores(
        question,
        k=5,
    )

    for i, (document, score) in enumerate(results, start=1):

        print(f"\n--- RESULT {i} ---")
        print("Similarity score:", round(score, 4))
        print("Page:", document.metadata.get("page"))
        print("Content:")
        print(document.page_content[:300])