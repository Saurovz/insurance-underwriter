insurance-underwriter/
├── .venv/
├── pyproject.toml
├── uv.lock           
├── main.py           # The entry point script │
└── src/
    └── insurance_underwriter/
        ├── core/                  # LangGraph State, Nodes, Graph assembly
        │   ├── state.py
        │   ├── nodes.py
        │   └── graph.py
        ├── data_ingestion/        # PDF extraction and schema
        │   ├── extraction_schema.py
        │   ├── pdf_loader.py
        │   └── ingestion_agent.py
        ├── config/                # Settings and rules
        │   ├── settings.py
        │   └── insurance_rules.py
        ├── utils/                 # LLM setup, file helpers
        │   ├── llm_setup.py
        │   └── helpers.py
        ├── tests/                 # Unit and integration tests
        │   └── test_full_graph.py
        │   └── test_ingestion.py
        │   └── test_pricing_logic.py
        └── __init__.py