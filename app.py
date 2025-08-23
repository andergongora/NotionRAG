from chatbot.core import MainApp
from chatbot.embeddings import EmbeddingNotion, RetrieverNotion

def main():
    # Initialize the main application
    app = MainApp()

    # Example query to run through the chatbot
    query = input("Escribe tu pregunta: ")

    # Run the application with the query
    app.run(query)

if __name__ == "__main__":
    main()
