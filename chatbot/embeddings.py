from langchain_community.document_loaders import NotionDirectoryLoader
from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

def EmbeddingNotion(filepath: Optional[str] = "data", persist_directory:
                    Optional[str] = "chroma_db", load: Optional[bool] = True, device:
                    Optional[str] = "cpu" ) -> Chroma:
    filepath = filepath or "data"
    persist_directory = persist_directory or "chroma_db"
    loader = NotionDirectoryLoader(filepath)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="HIT-TMG/KaLM-embedding-multilingual-mini-v1",
        model_kwargs={'device': device} # "cuda" if torch.cuda.is_available() else "cpu"
    )

    if not os.path.exists(persist_directory) or not load:
        os.makedirs(persist_directory, exist_ok=True)
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    else:
      # Load the persisted database
      vectordb = Chroma(
          persist_directory=persist_directory,
          embedding_function=embeddings
      )
    return vectordb

def RetrieverNotion(vectordb: Chroma, k: int = 5):
    # Create a retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}  # Return the top k most similar chunks
    )
    return retriever
