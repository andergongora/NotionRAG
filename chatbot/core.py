from chatbot.embeddings import EmbeddingNotion, RetrieverNotion
from chatbot.llm import Chatbot
import streamlit as st
import os
import dotenv
dotenv.load_dotenv()

@st.cache_resource
def load_embeddings(data_dir: str = 'data', persist_dir: str = 'chroma_db'):
    return EmbeddingNotion(
        filepath=data_dir,
        persist_directory=persist_dir,
        load=True,
        device="cuda" if os.environ.get('CUDA_VISIBLE_DEVICES') else "cpu"
    )


class MainApp:
    def __init__(self):
        self.vectordb = None
        self.gemini_api = ''

    def set_api(self, google_api_key):
        self.gemini_api = google_api_key

    def load_data(self, data_dir: str = 'data', persist_dir: str = 'chroma_db'):
        # Load embeddings and create a vector database
        self.vectordb = load_embeddings(data_dir, persist_dir)

        # Create a retriever from the vector database
        self.retriever = RetrieverNotion(self.vectordb, k=5)

        # Create a chatbot instance
        self.chatbot = Chatbot(model_name="gemini-1.5-flash", google_api_key=self.gemini_api)

        # Create a RAG chain using the retriever
        self.rag_chain = self.chatbot.create_rag_chain(self.retriever)


    def run(self, query: str):
        # Invoke the chain with the query
        response = self.chatbot.invoke_chain(self.rag_chain, query)

        # Print the response
        self.chatbot.print_response(response)
        return response
