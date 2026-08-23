from ingest import calculate_file_hash


pdf_path = "data/MongoDB Handbook.pdf"

file_hash = calculate_file_hash(
    pdf_path
)

print("File hash:")
print(file_hash)