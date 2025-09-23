import streamlit as st
from utils.utils import download_chroma_data, load_chroma_zip, process_notion_data, update_data, set_api


def Streamlit_App(app_class):
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
                    {"role": "assistant", "content": {"text": "How can I help you?", "sources": []}}
                ]
     # Initialize session state variables
    if "app" not in st.session_state:
        st.session_state["app"] = app_class()
    elif st.session_state["app"] is None:
        st.session_state["app"] = app_class()
    if "download_chroma" not in st.session_state:
        st.session_state['download_chroma'] = False

     # If there's an API key in session_state, ensure the new app instance gets it
    api_key = st.session_state.get("gemini_api_key")
    if api_key:
        try:
            st.session_state["app"].set_api(api_key)
            st.session_state["gemini_api_loaded"] = True
        except Exception:
            # ignore if app doesn't expose set_api for any reason
            pass

    with st.sidebar:
        if st.button("Cleanup & Reset"):
            # Perform cleanup
            if st.session_state["app"]:
                st.session_state["app"].cleanup()

            # Reset session state but don't touch file uploaders
            st.session_state["app"] = app_class()
            st.session_state["messages"] = [
                {"role": "assistant", "content": {"text": "How can I help you?", "sources": []}}
            ]
            st.session_state['download_chroma'] = False
            st.session_state['notion_loaded'] = False
            st.session_state['chroma_loaded'] = False

            st.toast("All data has been cleaned up. You can upload new files.", icon="✅")
            st.rerun()

        st.title("Gemini")
        st.text_input("Gemini API Key", key="gemini_api_key", type="password", on_change=lambda: set_api())
        st.caption("The API is FREE!")
        st.link_button("Get Gemini API","https://aistudio.google.com/u/1/apikey")
        st.markdown("---")
        st.title("Notion")
        notion_file = st.file_uploader("Insert Notion zip", type=".zip", key="notion_zip", on_change=lambda: update_data())
        if st.session_state.get("notion_zip") and not st.session_state.get("notion_loaded"):
            st.info("Notion file uploaded. Click 'Load data' to process it.")
        with st.expander("How to download"):
            st.write("To download, select your main page, click the top right three dots and click _export_.")
            st.write("Use this configuration:")
            st.image("./img/export_notion.png")
            st.write("You can try a tiny database here: https://andergongora.notion.site/Proyecto-Turismo-en-Valencia-0798f8fb92da49888d330b02ab755fd9")
        st.markdown("---")
        st.subheader("Chroma DB (persisted embeddings)")
        st.file_uploader("Upload chroma_db.zip to restore embeddings", type=["zip"], key="chroma_zip", on_change=load_chroma_zip)
        if st.session_state['download_chroma']:
            try:
                st.download_button(
                    label="Download ZIP",
                    data=download_chroma_data(),
                    file_name="chroma_db.zip",
                    mime="application/zip",
                    icon=":material/download:",
            )
            except Exception as e:
                st.error(f"Error downloading ZIP: {e}")
        st.markdown("---")
        st.button("Load data (build or load embeddings)", on_click=lambda: process_notion_data(st.session_state["app"]))
        st.markdown("---")
        st.subheader("Current Status")
        if st.session_state.get("gemini_api_loaded"):
            st.success("✓ Gemini API loaded")
        else:
            st.warning("✗ Gemini API not loaded")

        if st.session_state.get("notion_loaded") or st.session_state.get("chroma_loaded"):
            st.success("✓ Data loaded")
        else:
            st.warning("✗ Data not loaded")

        if st.session_state.get("download_chroma"):
            st.success("✓ Embeddings ready for download")
        else:
            st.info("Embeddings not yet built")
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
        app = st.session_state["app"]
        if not hasattr(app, "rag_chain") or app.rag_chain is None:
            st.warning("Please load data first by clicking 'Load data' button.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = st.session_state["app"].run(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
