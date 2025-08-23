├── README.md
├── requirements.txt
├── .gitignore
├── app/                     ← Frontend Streamlit
│   ├── streamlit_app.py
│   └── utils_streamlit.py
├── chatbot/                ← Lógica del chatbot
│   ├── __init__.py
│   ├── core.py            ← llamadas al modelo/API
│   ├── embeddings.py
│   ├── retriever.py
│   └── responses.py
├── data/                   ← Fuentes de datos
│   ├── raw/               ← datos originales (PDF, CSV…)
│   └── processed/         ← embeddings, vectordb, etc.
├── tests/                  ← Pruebas unitarias
│   └── test_core.py
├── docs/                   ← Documentación y diagramas
└── deploy/                 ← Docker / scripts de despliegue
