from loaders import load_pdf
from splitter import split_documents


pdf_path = "data/MongoDB Handbook.pdf"

documents = load_pdf(pdf_path)

chunks = split_documents(documents)

print("Number of documents:", len(documents))
print("Number of chunks:", len(chunks))

print("\n--- FIRST CHUNK ---")
print(chunks[0].page_content)

print("\n--- FIRST CHUNK METADATA ---")
print(chunks[0].metadata)

print("\n--- SECOND CHUNK ---")
print(chunks[1].page_content)