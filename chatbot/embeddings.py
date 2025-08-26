from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

def EmbeddingNotion(files: dict = None, persist_directory: str = "chroma_db", device: str = "cpu"):
    embeddings = HuggingFaceEmbeddings(
        model_name="HIT-TMG/KaLM-embedding-multilingual-mini-v1",
        model_kwargs={'device': device}
    )

    # Si ya existe persist_directory con contenido, lo cargamos directamente
    if persist_directory and os.path.exists(persist_directory) and os.listdir(persist_directory):
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return vectordb

    # Si no hay persistente, pero tenemos 'files', creamos vectordb desde los documentos
    if not files:
        raise ValueError("No files provided to build embeddings and no persisted DB found.")

    docs = []
    for filename, content in files.items():
        if filename.endswith(".md") or filename.endswith(".txt"):
            docs.append(Document(page_content=content.decode("utf-8"), metadata={"source": filename}))
        elif filename.endswith(".html"):
            from bs4 import BeautifulSoup
            text = BeautifulSoup(content, "html.parser").get_text()
            docs.append(Document(page_content=text, metadata={"source": filename}))
        else:
            # puedes ampliar el parsing según tipos que exporate Notion
            try:
                docs.append(Document(page_content=content.decode("utf-8"), metadata={"source": filename}))
            except Exception:
                # ignorar ficheros no textuales
                continue

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory  # persistimos para futuras cargas
    )
    return vectordb


def RetrieverNotion(vectordb: Chroma, k: int = 5):
    # Create a retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}  # Return the top k most similar chunks
    )
    return retriever
