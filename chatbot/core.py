from chatbot.embeddings import EmbeddingNotion, RetrieverNotion
from chatbot.llm import Chatbot
import streamlit as st
import os
import shutil
import dotenv
import torch
dotenv.load_dotenv()

@st.cache_resource(show_spinner=False)
def get_vectordb_or_build(files, persist_dir, device):
    return EmbeddingNotion(files, persist_directory=persist_dir, device=device)

class MainApp:
    def __init__(self):
        self.vectordb = None
        self.gemini_api = ''
        self.chatbot = None
        self.retriever = None
        self.rag_chain = None
        self.persist_dir = "chroma_db"

    def set_api(self, google_api_key):
        self.gemini_api = google_api_key

    def ensure_chatbot(self):
        """
        Crea la instancia del chatbot si no existe y hay una API key.
        """
        if self.chatbot is None:
            if not self.gemini_api:
                raise ValueError("No API key set for chatbot.")
            # Chatbot acepta google_api_key como primer arg o por keyword
            self.chatbot = Chatbot(google_api_key=self.gemini_api, model_name="gemini-1.5-flash")

    def load_data(self):

        self.ensure_chatbot()

        files = st.session_state.get("notion_files")
        persist_has_content = os.path.exists(self.persist_dir) and os.listdir(self.persist_dir)

        # Prefer using an existing persisted Chroma DB if present
        if persist_has_content:
            st.toast("Using persisted Chroma DB embeddings.", icon="✅")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.vectordb = get_vectordb_or_build(files=None, persist_dir=self.persist_dir, device=device)
        elif files:
            # Build new embeddings from Notion files
            if not os.path.exists(self.persist_dir):
                os.makedirs(self.persist_dir, exist_ok=True)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.vectordb = get_vectordb_or_build(files=files, persist_dir=self.persist_dir, device=device)
            st.session_state['download_chroma'] = True
        else:
            raise ValueError("No data found. Upload Notion ZIP or Chroma DB ZIP and click Load data.")

        self.retriever = RetrieverNotion(self.vectordb, k=5)
        self.rag_chain = self.chatbot.create_rag_chain(self.retriever)

    def run(self, query: str):
        if self.chatbot is None or self.rag_chain is None:
            raise RuntimeError("Chatbot or RAG chain not initialized. Load data first.")
        # Invoke the chain with the query
        response = self.chatbot.invoke_chain(self.rag_chain, query)

        # Print the response
        self.chatbot.print_response(response)
        return response

    def cleanup(self):
        """Clean up resources and remove ChromaDB data"""
        # Clear in-memory objects
        self.vectordb = None
        self.chatbot = None
        self.retriever = None
        self.rag_chain = None
        # Remove ChromaDB directory if it exists
        if os.path.exists(self.persist_dir):
            try:
                shutil.rmtree(self.persist_dir)
                print(f"Removed ChromaDB directory: {self.persist_dir}")
            except Exception as e:
                print(f"Error removing ChromaDB directory: {e}")
                # If we can't remove it, at least try to delete the collection
                if self.vectordb:
                    try:
                        self.vectordb.delete_collection()
                    except:
                        pass
