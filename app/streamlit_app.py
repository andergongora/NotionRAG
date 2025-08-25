import io
import streamlit as st
from utils.utils import download_chroma_data, process_notion_data, update_data, set_api


def Streamlit_App(app_class):
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
                    {"role": "assistant", "content": {"text": "How can I help you?", "sources": []}}
                ]
    if "app" not in st.session_state:
        st.session_state["app"] = app_class()
    if "download_chroma" not in st.session_state:
        st.session_state['download_chroma'] = False

    with st.sidebar:
        st.title("Gemini")
        st.text_input("Gemini API Key", key="gemini_api_key", type="password", on_change=lambda: set_api())
        st.caption("The API is FREE!")
        st.link_button("Get Gemini API","https://aistudio.google.com/u/1/apikey")
        st.title("Notion")
        st.file_uploader("Insert Notion zip", type=".zip", key="notion_zip", on_change=lambda: update_data())
        if st.session_state['download_chroma']:
            st.download_button(
                label="Download ZIP",
                data=download_chroma_data(),
                file_name="chroma_db.zip",
                mime="application/zip",
                icon=":material/download:",
            )

        with st.expander("How to download"):
            st.write("To download, select your main page, click the top right three dots and click _export_.")
            st.write("Use this configuration:")
            st.image("./img/export_notion.png")
        st.button("Load data", on_click=lambda: process_notion_data(st.session_state["app"]))
    st.title("💬 Notion Chatbot")
    st.caption("🚀 Created by Ander Góngora ☺️")
    for msg in st.session_state.messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            # contenido de usuario: si no es string, lo mostramos como str (sin mutar)
            with st.chat_message("user"):
                st.write(content if isinstance(content, str) else str(content))

        elif role == "assistant":
            # manejamos distintos tipos sin modificar session_state:
            text = ""
            sources = []

            # si es el formato nuevo esperado
            if isinstance(content, dict) and "text" in content:
                text = content.get("text", "")
                sources = content.get("sources", [])
            # si viene como dict pero con otras keys (mensaje antiguo), lo mostramos de forma segura (sin cambiar)
            elif isinstance(content, dict):
                text = content.get("result") or content.get("text") or content.get("message") or ""
                # si no hay texto, volcamos el dict resumido
                if not text:
                    text = str(content)
                # intentar extraer fuentes si existen
                sources = content.get("source_documents") or content.get("sources") or []
            # si viene como string
            elif isinstance(content, str):
                text = content
                sources = []
            # si viene lista (posible conjunto de fuentes antiguas)
            elif isinstance(content, list):
                text = ""
                sources = content
            else:
                text = str(content)
                sources = []

            with st.chat_message("assistant"):
                st.write(text)

            if sources:
                with st.expander("Fuentes:"):
                    for s in sources:
                        # si es un objeto tipo documento con page_content
                        if hasattr(s, "page_content"):
                            st.markdown(s.page_content or "")
                        else:
                            st.markdown(str(s))

    if prompt := st.chat_input():
        if not hasattr(st.session_state["app"], "chatbot"):
            st.warning("Please upload your Notion file first.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = st.session_state["app"].run(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
