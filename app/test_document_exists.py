from vectorstore import get_vectorstore


DOCUMENT_ID = "8dc12f1f-57e2-4c6b-9fda-9484f10604e3"


vectorstore = get_vectorstore()


results = vectorstore.get(
    where={
        "document_id": DOCUMENT_ID
    }
)


ids = results.get("ids", [])


print("\n==============================")
print("CHROMA VERIFICATION")
print("==============================")


print(
    f"Remaining chunks for document: {len(ids)}"
)


if len(ids) == 0:

    print(
        "✅ Document vectors successfully deleted."
    )

else:

    print(
        "❌ Document vectors still exist."
    )

    print(ids)