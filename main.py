from chatbot.core import MainApp
from app.streamlit_app import Streamlit_App

def main():
    # Initialize the main application
    Streamlit_App(MainApp)
    # Example query to run through the chatbot
    # query = input("Escribe tu pregunta: ")

    # Run the application with the query
    # app.run(query)

if __name__ == "__main__":
    main()
