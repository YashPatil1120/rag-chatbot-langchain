from loaders import load_document


file_path = "data/text.docx"

print("=" * 60)
print(f"TESTING: {file_path}")
print("=" * 60)

try:

    documents = load_document(file_path)

    print(f"Loaded documents: {len(documents)}")

    for i, document in enumerate(documents):

        print(f"\n--- DOCUMENT {i + 1} ---")
        print(repr(document.page_content))
        print("\nMetadata:")
        print(document.metadata)

except Exception as error:

    print(f"ERROR: {error}")