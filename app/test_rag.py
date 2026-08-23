from rag import ask_question


questions = [
    "What is MongoDB?",
    "What is mongosh?",
    "How does aggregation work?",
    "What is the capital of France?",
]


for question in questions:

    print("\n")
    print("=" * 70)
    print("QUESTION")
    print("=" * 70)

    print(question)


    response, documents, standalone_question = (
        ask_question(question)
    )


    print("\n")
    print("=" * 70)
    print("RETRIEVAL QUERY")
    print("=" * 70)

    print(
        standalone_question
    )


    print("\n")
    print("=" * 70)
    print("ANSWER")
    print("=" * 70)


    if response is None:

        print(
            "I don't know based on "
            "the provided document."
        )

    else:

        print(
            response.text
        )


    print("\n")
    print("=" * 70)
    print("SOURCES")
    print("=" * 70)


    if not documents:

        print(
            "No sources."
        )

    else:

        for index, document in enumerate(
            documents,
            start=1,
        ):

            print(
                f"\nSource {index}"
            )

            print(
                "File:",
                document.metadata.get(
                    "file_name"
                ),
            )

            print(
                "Page:",
                document.metadata.get(
                    "page"
                ),
            )

            print(
                "Content:"
            )

            print(
                document.page_content[:300]
            )