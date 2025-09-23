NotionRAG (Streamlit + Gemini + Chroma)

[En Español](#espanol)

RAG (Retrieval Augmented Generation) chatbot to chat with content exported from Notion. It uses Streamlit for the UI, Google Gemini as the LLM, and ChromaDB to persist embeddings.

- Load a Notion export ZIP and build embeddings.
- Load a prebuilt `chroma_db.zip` to skip the build step.
- Download `chroma_db.zip` for later reuse.

## Requirements

- Python 3.10+ (recommended)
- Gemini API key
- Optional: CUDA-capable GPU (auto-detected; CPU is used otherwise)

## Project structure

```
.
├── app/
│   └── streamlit_app.py
├── chatbot/
│   ├── core.py
│   ├── embeddings.py
│   └── llm.py
├── chroma_db/                  ← persistence folder; created/filled at runtime
├── img/
│   └── export_notion.png
├── utils/
│   └── utils.py
├── main.py
├── requirements.txt
└── README.md
```

## Installation

1) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows (PowerShell)
```

2) Install dependencies via `requirements.txt`:

```bash
pip install -U pip
pip install -r requirements.txt
```

If `requirements.txt` is not available, install key packages manually:

```bash
pip install streamlit langchain langchain-google-genai langchain-chroma langchain-huggingface beautifulsoup4 chromadb torch python-dotenv
```

## Gemini API configuration

You can paste the API key directly in the Streamlit sidebar. Optionally, create a `.env` file at the project root:

```
GOOGLE_API_KEY=your_gemini_api_key
```

Modules load `dotenv` on startup.

## Run (Streamlit)

From the project root:

```bash
streamlit run app/streamlit_app.py
```

In the sidebar:

1. Enter your Gemini API key (the "Get Gemini API" button helps you obtain one).
2. Under "Notion", upload the exported `.zip` from Notion, or under "Chroma DB" upload a prebuilt `chroma_db.zip`.
3. Click "Load data (build or load embeddings)" to build or load embeddings.
4. Start chatting in the main chat area.

Notes:

- After building embeddings from Notion, a button appears to download `chroma_db.zip`. Keep it for faster future loads.
- The "Cleanup & Reset" button resets session state, removes the `chroma_db` folder, and lets you start over.

## Exporting from Notion

1. Open your root page in Notion.
2. Click the three dots (top-right) → "Export".
3. Export as Markdown/HTML (the app supports `.md`, `.txt`, and `.html`).
4. Upload the resulting ZIP to the app.

A visual example is shown in `app/streamlit_app.py` under the "How to download" expander.

## How it works (high-level)

- `chatbot/embeddings.py`: splits documents into chunks and creates/loads embeddings with `HuggingFaceEmbeddings` and `Chroma` (persisted in `chroma_db/`).
- `chatbot/llm.py`: configures Gemini and a `RetrievalQA` chain (Spanish prompt by default; easy to customize).
- `chatbot/core.py`: orchestrates data loading, retriever setup, and the RAG chain lifecycle.
- `utils/utils.py`: Streamlit logic for uploading ZIPs, building/loading, and downloading `chroma_db.zip`.
- `app/streamlit_app.py`: chat UI and sidebar (API key, uploads, state, actions).

## Using the interface

- Status indicators show API readiness, data loaded, and whether an embeddings ZIP is available.
- Chat: type your question; the assistant answers. When available, source chunks are shown in an expandable section.

## Troubleshooting

- API not loading: paste the key in the sidebar or set `GOOGLE_API_KEY` in the environment. If you change the key, load it again.
- Invalid Notion ZIP: export from the correct page and avoid password-protected ZIPs. Empty files are skipped.
- Invalid `chroma_db.zip`: it must contain Chroma files (e.g., `chroma.sqlite3`, `chroma-collections.parquet`, `chroma-embeddings.parquet`). The app will warn and clean the folder otherwise.
- Deleting `chroma_db` fails: close processes using the folder. The app retries deletion; if it still fails, delete manually.
- GPU vs CPU: if CUDA is unavailable, CPU is used automatically. Building embeddings on CPU may take longer.

## Command-line run (optional)

`main.py` programmatically initializes the Streamlit app, but the recommended flow is `streamlit run app/streamlit_app.py` for the full UI.

## License

This project is provided for educational purposes. Adjust the license as needed.

---

## Español <a id="espanol"></a>

NotionRAG (Streamlit + Gemini + Chroma)

Proyecto de RAG (Retrieval Augmented Generation) para chatear con contenido exportado de Notion. Usa Streamlit como interfaz, Google Gemini como LLM y ChromaDB para persistir embeddings. Permite:

- Cargar un ZIP exportado de Notion y construir embeddings.
- Cargar un `chroma_db.zip` ya generado para saltar la fase de construcción.
- Descargar el `chroma_db.zip` para reutilizarlo más tarde.

## Requisitos

- Python 3.10+ recomendado
- Cuenta y API Key de Gemini
- Opcional: GPU con CUDA (el código detecta automáticamente; en caso contrario usa CPU)

## Estructura del proyecto

```
.
├── app/
│   └── streamlit_app.py
├── chatbot/
│   ├── core.py
│   ├── embeddings.py
│   └── llm.py
├── chroma_db/                  ← (carpeta de persistencia; se crea/llena en runtime)
├── img/
│   └── export_notion.png
├── utils/
│   └── utils.py
├── main.py
└── README.md
```

## Instalación

1) Clona el repositorio y crea un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows (PowerShell)
```

2) Instala dependencias. Si existe `requirements.txt`, usa:

```bash
pip install -U pip
pip install -r requirements.txt
```

Si no, instala los paquetes clave manualmente:

```bash
pip install streamlit langchain langchain-google-genai langchain-chroma langchain-huggingface beautifulsoup4 chromadb torch python-dotenv
```

## Configuración de la API de Gemini

No es obligatorio crear `.env`, ya que la app permite pegar la API key desde la barra lateral. Si prefieres variables de entorno, puedes crear un archivo `.env` en la raíz con:

```
GOOGLE_API_KEY=tu_api_key_de_gemini
```

Los módulos cargan `dotenv` al iniciar.

## Ejecución (Streamlit)

Desde la raíz del proyecto:

```bash
streamlit run app/streamlit_app.py
```

En la barra lateral:

1. Introduce tu Gemini API Key (botón "Get Gemini API" te lleva a obtenerla).
2. En "Notion", sube el archivo `.zip` exportado desde Notion o, alternativamente, en "Chroma DB" sube un `chroma_db.zip` previamente generado.
3. Pulsa "Load data (build or load embeddings)" para construir o cargar los embeddings.
4. Comienza a chatear en la parte central de la app.

Notas:

- Tras construir embeddings desde Notion, aparecerá un botón para descargar `chroma_db.zip`. Guárdalo para cargas futuras más rápidas.
- El botón "Cleanup & Reset" limpia el estado, elimina la carpeta `chroma_db` y te permite empezar de cero.

## Cómo exportar desde Notion

1. Abre tu página raíz en Notion.
2. Haz clic en los tres puntos (arriba a la derecha) → "Export".
3. Exporta como Markdown/HTML (la app soporta `.md`, `.txt` y `.html`).
4. Sube el ZIP resultante a la app.

En `app/streamlit_app.py` hay un ejemplo visual bajo el desplegable "How to download".

## Funcionamiento interno (resumen)

- `chatbot/embeddings.py`: divide documentos en chunks y crea/recupera embeddings con `HuggingFaceEmbeddings` y `Chroma` (persistidos en `chroma_db/`).
- `chatbot/llm.py`: prepara el LLM de Gemini y un `RetrievalQA` con prompt en español.
- `chatbot/core.py`: orquesta carga de datos, creación del retriever y la cadena RAG.
- `utils/utils.py`: lógica de Streamlit para subir ZIPs, construir/cargar y descargar `chroma_db.zip`.
- `app/streamlit_app.py`: interfaz de chat y barra lateral (API Key, cargas, estados y acciones).

## Uso de la interfaz

- Estado actual: se muestran indicadores de API, datos cargados y disponibilidad del ZIP de embeddings.
- Chat: escribe tu pregunta; el asistente responderá en español. Si hay fuentes, se pueden ver en un desplegable.

## Solución de problemas

- No se carga la API: asegúrate de pegar la key en la barra lateral o de tener `GOOGLE_API_KEY` en el entorno. Si cambias la key, pulsa de nuevo para cargarla.
- ZIP de Notion inválido: exporta desde la página correcta y sin proteger el ZIP con contraseña. La app ignora archivos vacíos.
- `chroma_db.zip` inválido: debe contener ficheros de Chroma (p. ej. `chroma.sqlite3`, `chroma-collections.parquet`, `chroma-embeddings.parquet`). Si no, la app avisará y limpiará la carpeta.
- Permisos al borrar `chroma_db`: cierra procesos que usen la carpeta. La app intenta borrar con reintentos; si falla, bórrala manualmente.
- GPU/CPU: si no hay CUDA disponible, se usará CPU automáticamente. En máquinas sin GPU, la construcción de embeddings puede tardar más.

## Ejecución por línea de comandos (opcional)

El archivo `main.py` inicializa la app Streamlit programáticamente, pero el flujo recomendado es usar `streamlit run app/streamlit_app.py` para la interfaz completa.

## Licencia

Este proyecto se distribuye con fines educativos. Ajusta la licencia según tus necesidades.
