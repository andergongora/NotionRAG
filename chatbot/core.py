from chatbot.embeddings import EmbeddingNotion, RetrieverNotion
from chatbot.llm import Chatbot
import streamlit as st
import dotenv
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
        if not files:
            raise ValueError("No Notion data loaded")
        
        self.vectordb = get_vectordb_or_build(files=files, persist_dir="chroma_db", device="cpu")
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
