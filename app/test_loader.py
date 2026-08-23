from loaders import load_pdf


pdf_path = "data/MongoDB Handbook.pdf"

documents = load_pdf(pdf_path)

print("Number of usable documents/pages:", len(documents))

print("\n--- FIRST USABLE DOCUMENT ---")
print(documents[0].page_content)

print("\n--- METADATA ---")
print(documents[0].metadata)