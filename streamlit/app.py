import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="EchoPulse", layout="centered")

st.title("EchoPulse")
st.caption("Streamlit · n8n · MCP · PostgreSQL")

MERMAID = """
flowchart LR
    ST[Streamlit]
    ING[Ingest]
    AGT[Analyst]
    LLM[OpenRouter]
    MCP[MCP Server]
    DB[(PostgreSQL)]

    ST --> ING & AGT
    ING --> LLM --> DB
    AGT --> LLM
    AGT <--> MCP --> DB

    classDef ui fill:#6366f1,stroke:#4f46e5,color:#fff
    classDef flow fill:#f97316,stroke:#ea580c,color:#fff
    classDef ai fill:#a855f7,stroke:#9333ea,color:#fff
    classDef data fill:#0ea5e9,stroke:#0284c7,color:#fff

    class ST ui
    class ING,AGT flow
    class LLM,MCP ai
    class DB data
"""

components.html(
    f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <div class="mermaid">{MERMAID}</div>
    <script>mermaid.initialize({{ startOnLoad: true, theme: "dark" }});</script>
    """,
    height=220,
)

st.markdown("Use the sidebar to **submit reviews** or **chat with the analyst**.")
