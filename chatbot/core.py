from chatbot.embeddings import EmbeddingNotion, RetrieverNotion
from chatbot.llm import Chatbot
import os
import dotenv
dotenv.load_dotenv()

class MainApp:
    def __init__(self):
        # Load embeddings and create a vector database
        self.vectordb = EmbeddingNotion(
            filepath="data",
            persist_directory="chroma_db",
            load=True,
            device="cuda" if os.environ.get('CUDA_VISIBLE_DEVICES') else "cpu"
        )

        # Create a retriever from the vector database
        self.retriever = RetrieverNotion(self.vectordb, k=5)

        # Create a chatbot instance
        self.chatbot = Chatbot(model_name="gemini-1.5-flash")

        # Create a RAG chain using the retriever
        self.rag_chain = self.chatbot.create_rag_chain(self.retriever)

    def run(self, query: str):
        # Invoke the chain with the query
        response = self.chatbot.invoke_chain(self.rag_chain, query)

        # Print the response
        self.chatbot.print_response(response)

