import os
from langchain.embeddings import init_embeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


VECTOR_DB_DIR = "chroma_db"
COLLECTION_NAME = "sunbeam_data"

os.makedirs(VECTOR_DB_DIR, exist_ok=True)
 
embed_model = init_embeddings(
    model="nomic-ai/nomic-embed-text-v1.5-GGUF",
    provider="openai",
    base_url="http://10.161.130.59:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)
 
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embed_model,
    persist_directory=VECTOR_DB_DIR
)
 
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


def store_to_chroma():
    if not os.path.exists("datascraping.txt"):
        print("ERROR: datascraping.txt not found")
        return

    with open("datascraping.txt", "r", encoding="utf-8") as f:
        text = f.read()

    documents = []
    for chunk in splitter.split_text(text):
        documents.append(
            Document(
                page_content=chunk,
                metadata={"source": "sunbeam"}
            )
        )

    vectorstore.add_documents(documents)
    vectorstore.persist()

    print("Embeddings stored successfully.")
    print("Total documents:", vectorstore._collection.count())


if __name__ == "__main__":
    store_to_chroma()

