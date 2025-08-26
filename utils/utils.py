import streamlit as st
import zipfile
import io
import os
import shutil

zipfile_chroma_name = "chroma_db.zip"
data_dir = "data"
persist_dir = "chroma_db"

def update_data():
    uploaded = st.session_state.get("notion_zip")
    if uploaded is None:
        return
    with zipfile.ZipFile(io.BytesIO(uploaded.getvalue())) as z:
        st.session_state["notion_files"] = {
            name: z.read(name) for name in z.namelist() if not name.endswith("/")
        }
    st.toast("Successfully loaded Notion data.", icon="✅")
    st.session_state["notion_loaded"] = True


def set_api():
    api_key = st.session_state.get("gemini_api_key", "")
    app = st.session_state.get("app")
    if not app:
        st.toast("App instance not initialized.", icon="⚠️")
        return
    if not api_key:
        st.toast("Please input an API key.", icon="⚠️")
        return
    app.set_api(api_key)
    st.toast("Successfully loaded Gemini API.", icon="✅")
    st.session_state["gemini_api_loaded"] = True



def process_notion_data(app):
    exit_process = False
    api_g = st.session_state.get('gemini_api_key')
    if st.session_state.get('notion_zip')==None:
        st.toast("Load Notion zip first.", icon='⚠️')
        exit_process=True
    if api_g==None or api_g=="":
        st.toast("Load Gemini API first.", icon='⚠️')
        exit_process=True
    if exit_process:
        return

    st.toast("Building / loading embeddings. This may take a while...", icon="🔃")
    app.load_data()
    st.session_state['download_chroma'] = True
    st.toast("Embeddings ready.", icon="✅")


def download_chroma_data():
    buffer = io.BytesIO()
    if not os.path.exists(persist_dir):
        raise FileNotFoundError("Persist directory not found. Build embeddings first.")
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        for folder_path, _, files in os.walk(persist_dir):
            for file in files:
                complete_route = os.path.join(folder_path, file)
                relative_path = os.path.relpath(complete_route, persist_dir)
                zout.write(complete_route, relative_path)
    
    buffer.seek(0)
    return buffer

def load_chroma_zip():
    uploaded = st.session_state.get("chroma_zip")
    if uploaded is None:
        return
    # limpiar persist_dir previo (con cuidado)
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
    os.makedirs(persist_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(uploaded.getvalue())) as z:
        z.extractall(path=persist_dir)

    st.toast("Chroma DB loaded from ZIP.", icon="✅")
    st.session_state["chroma_loaded"] = True
