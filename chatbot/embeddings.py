from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from bs4 import BeautifulSoup
import streamlit as st
import os
import shutil
import time


def safe_remove_directory(path, max_retries=5):
    """Safely remove a directory with retries"""
    for i in range(max_retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return True
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(0.5)  # Wait before retrying
                continue
            else:
                print(f"Failed to remove directory {path} after {max_retries} attempts: {e}")
                return False
    return False

def fix_permissions(directory):
    """Recursively fix permissions on directory and contents"""
    try:
        os.chmod(directory, 0o755)  # drwxr-xr-x for directories
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o666)  # rw-rw-rw- for files
    except Exception as e:
        print(f"Warning: Could not set permissions: {e}")

def EmbeddingNotion(files: dict = None, persist_directory: str = "chroma_db", device: str = "cpu"):
    ## If we have files to process, clean up the existing directory
    if files and os.path.exists(persist_directory):
        safe_remove_directory(persist_directory)

    # Ensure the directory exists
    os.makedirs(persist_directory, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name="HIT-TMG/KaLM-embedding-multilingual-mini-v1",
        model_kwargs={'device': device}
    )

    # Si ya existe persist_directory con contenido, lo cargamos directamente
    # If DB exists and has content, try to load it
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
                return vectordb
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retrying
                    continue
                else:
                    # If all retries fail, rebuild the database
                    print(f"Failed to load existing database: {e}. Rebuilding...")
                    safe_remove_directory(persist_directory)
                    break

    # Si no hay persistente, pero tenemos 'files', creamos vectordb desde los documentos
    if not files:
        raise ValueError("No files provided to build embeddings and no persisted DB found.")

    docs = []
    for filename, content in files.items():
        try:
            if filename.endswith(".md") or filename.endswith(".txt"):
                text = content.decode("utf-8")
            elif filename.endswith(".html"):
                text = BeautifulSoup(content, "html.parser").get_text()
            else:
                text = content.decode("utf-8")

            # Skip empty documents
            if not text.strip():
                continue

            docs.append(Document(page_content=text, metadata={"source": filename}))
        except Exception:
            continue
    if not docs:
        raise ValueError("No valid text documents found in the uploaded files.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    if not chunks:
        raise ValueError("No valid text chunks created from documents.")

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
