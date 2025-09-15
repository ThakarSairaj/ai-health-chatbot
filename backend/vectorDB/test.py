# File: vectorDB/test.py

import chromadb

def get_brain_collection(path="./brain_medical_database", name="brain_anatomy"):
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(name=name)


def search_brain_knowledge(question: str, n_results: int = 3):
    collection = get_brain_collection()

    print("🔎 Querying ChromaDB...")
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    return results


if __name__ == "__main__":
    print("🧠 TESTING YOUR BRAIN RAG SYSTEM")
    print("=" * 40)

    question = "What are the main parts of the brain and what functions does each control?"
    print(f"\n❓ Question: {question}")

    try:
        results = search_brain_knowledge(question)

        print("\n📄 Top Results:")
        for i, doc in enumerate(results['documents'][0]):
            print(f"\n🔹 Result {i+1}:")
            print(doc)

    except Exception as e:
        print(f"❌ Error querying ChromaDB: {e}")
