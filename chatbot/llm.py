from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import dotenv
dotenv.load_dotenv()

class Chatbot:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.template = """Eres un asistente de inteligencia artificial útil. Usa los siguientes fragmentos de contexto para responder la pregunta al final.
Si no sabes la respuesta, simplemente di que no la sabes. No inventes una respuesta.

Contexto:
{context}

Pregunta: {question}

Respuesta:
"""
        self.prompt = PromptTemplate(
            template=self.template,
            input_variables=["context", "question"]
        )

    def create_rag_chain(self, retriever) -> RetrievalQA:
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )

    def invoke_chain(self, rag_chain, query: str) -> dict:
        response = rag_chain.invoke({"query": query})
        return response

    def print_response(self, response) -> None:
        print("Pregunta:", response["query"])
        print("Respuesta:\n", response["result"])
        print("\nFuentes:\n")

        sources = set()
        for doc in response["source_documents"]:
            meta = doc.metadata
            source = meta.get("source") or meta.get("file_path") or "Documento sin nombre"
            contenido = doc.page_content or "Contenido no disponible"
            sources.add(source + '\n' + contenido)

        for i, src in enumerate(sources, 1):
            print(f"{i}. {src}")
