from vectorstore import create_vectorstore


pdf_path = "data/MongoDB Handbook.pdf"

vectorstore = create_vectorstore(pdf_path)

print("Vector store created successfully!")