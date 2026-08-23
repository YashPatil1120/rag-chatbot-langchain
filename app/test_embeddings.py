from embeddings import embeddings


text = "MongoDB is a NoSQL document-oriented database."

vector = embeddings.embed_query(text)

print("Vector type:", type(vector))
print("Vector dimensions:", len(vector))
print("\nFirst 10 values:")
print(vector[:10])