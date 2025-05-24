"""Agent setup and management for the municipal data chatbot."""

import streamlit as st

from agents.factory import create_csv_chatbot_agent
from config import CSV_FILES


@st.cache_resource(show_spinner=False)
def get_agent():
    """Create and cache the CSV agent using the shared factory."""
    return create_csv_chatbot_agent(CSV_FILES, use_memory=True)
