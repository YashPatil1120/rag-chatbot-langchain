from ingest import ingest_pdf


pdf_path = "data/MongoDB Handbook.pdf"

result = ingest_pdf(
    pdf_path=pdf_path,
    original_filename="MongoDB Handbook.pdf",
)

print("\n==============================")
print("INGESTION RESULT")
print("==============================")

print("Document ID:", result["document_id"])
print("Filename:", result["filename"])
print("Pages:", result["pages"])
print("Chunks:", result["chunks"])