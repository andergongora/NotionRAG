import streamlit as st
import zipfile
import io
import os

zipfile_chroma_name = "chroma_db.zip"
data_dir = "data"
persist_dir = "chroma_db"

def update_data():
    uploaded = st.session_state.get("notion_zip")
    if uploaded==None:
        return
    zipfile.ZipFile(io.BytesIO(uploaded.getvalue())).extractall(path="data")
    st.toast("Successfully loaded Notion data.", icon="✅")


def set_api():
    st.session_state["app"].set_api(st.session_state["gemini_api_key"])
    st.toast("Successfully loaded Gemini API.", icon="✅")



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
    st.toast("LOADING")
    app.load_data(data_dir=data_dir, persist_dir=persist_dir)
    st.session_state['download_chroma'] = True

def download_chroma_data():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        for folder_path, _, files in os.walk(persist_dir):
            for file in files:
                complete_route = os.path.join(folder_path, file)
                relative_path = os.path.relpath(complete_route, persist_dir)
                zout.write(complete_route, relative_path)
    
    buffer.seek(0)
    return buffer
