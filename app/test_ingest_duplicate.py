from ingest import ingest_pdf


pdf_path = "data/MongoDB Handbook.pdf"


result = ingest_pdf(
    pdf_path=pdf_path,
    original_filename="MongoDB Handbook.pdf",
)


print("\n==============================")
print("RESULT")
print("==============================")

print(result)