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

    has_chroma = st.session_state.get('chroma_loaded', False)
    has_notion = st.session_state.get('notion_zip') is not None

    if not has_chroma and not has_notion:
        st.toast("Load Notion zip or Chroma DB first.", icon='⚠️')
        exit_process = True

    if api_g is None or api_g == "":
        st.toast("Load Gemini API first.", icon='⚠️')
        exit_process = True

    if exit_process:
        return

    try:
        # Create three columns to center the content
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Add some vertical spacing
            st.markdown("<br>" * 2, unsafe_allow_html=True)

            # Custom CSS for larger text and centered content
            st.markdown("""
                <style>
                    .big-text {
                        font-size: 20px;
                        text-align: center;
                        padding: 20px;
                        background-color: #f0f2f6;
                        border-radius: 10px;
                        margin: 20px 0;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Create a placeholder for the processing message
            message_placeholder = st.empty()
            
            # Display the message in the placeholder
            message_placeholder.markdown("""<div class="big-text">🔄 Processing documents and building embeddings...</br></br>
This may take several minutes on first load.</br></br>
💡 <strong>Tip:</strong> Download the chroma_db.zip after processing for faster loading next time!</div>""", unsafe_allow_html=True)

            # Process the data
            with st.spinner(""):
                app.load_data()
                st.session_state['download_chroma'] = True

            # Clear the message after processing
            message_placeholder.empty()
            st.toast("Embeddings ready!", icon="✅")
    except ValueError as e:
        st.error(f"Error processing documents: {str(e)}")
        st.toast("Failed to process data.", icon="❌")
        st.session_state['download_chroma'] = False


def download_chroma_data():
    buffer = io.BytesIO()
    if not os.path.exists(persist_dir):
        raise FileNotFoundError("Persist directory not found. Build embeddings first.")
    # Check if it's a valid Chroma DB
    required_files = ["chroma.sqlite3", "chroma-collections.parquet", "chroma-embeddings.parquet"]
    has_required_files = any(os.path.exists(os.path.join(persist_dir, f)) for f in required_files)

    if not has_required_files:
        raise ValueError("The Chroma database appears to be empty or invalid")

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
            for folder_path, _, files in os.walk(persist_dir):
                for file in files:
                    complete_route = os.path.join(folder_path, file)
                    relative_path = os.path.relpath(complete_route, persist_dir)
                    zout.write(complete_route, relative_path)
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise Exception(f"Error creating ZIP file: {str(e)}")

def load_chroma_zip():
    uploaded = st.session_state.get("chroma_zip")
    if uploaded is None:
        return

    try:
        # If there's an app in memory, clean it up first (so cleanup doesn't remove the newly extracted files)
        if "app" in st.session_state and st.session_state["app"]:
            st.session_state["app"].cleanup()
            st.session_state["app"] = None

        # Clean up existing directory and prepare persist_dir
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
        os.makedirs(persist_dir, exist_ok=True)

        # Extract the uploaded ZIP
        with zipfile.ZipFile(io.BytesIO(uploaded.getvalue())) as z:
            z.extractall(path=persist_dir)

        # Verify the extracted content is a valid Chroma DB
        required_files = ["chroma.sqlite3", "chroma-collections.parquet", "chroma-embeddings.parquet"]
        has_required_files = any(os.path.exists(os.path.join(persist_dir, f)) for f in required_files)

        if not has_required_files:
            st.error("Uploaded ZIP doesn't appear to contain a valid Chroma database")
            shutil.rmtree(persist_dir)
            return

        st.toast("Chroma DB loaded from ZIP.", icon="✅")
        st.session_state["chroma_loaded"] = True

    except Exception as e:
        st.error(f"Error loading Chroma DB: {str(e)}")
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)