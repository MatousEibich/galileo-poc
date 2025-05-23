"""UI components for the municipal data chatbot."""

import streamlit as st
from config import APP_TITLE, APP_ICON, LOGO_PATH


def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE, 
        page_icon=APP_ICON, 
        layout="wide"
    )


def render_sidebar() -> bool:
    """Render the sidebar with logo, quick buttons, and options.
    
    Returns:
        bool: Whether to show agent thoughts
    """
    with st.sidebar:
        st.image(LOGO_PATH, width=160, caption="Město Horšovský Týn")
        st.markdown("##### Chatbot městských dat")

        st.divider()

        st.markdown("**Rychlé dotazy:**")
        if st.button(":building_construction: Úřední deska"):
            st.session_state["preset_query"] = "Co je aktuálně na úřední desce?"
        if st.button(":houses: Bytové informace"):
            st.session_state["preset_query"] = "Jak funguje přidělování bytů v majetku města?"
        if st.button(":euro: Dotace z EU"):
            st.session_state["preset_query"] = "Jaké projekty jsou financovány z EU?"

        st.divider()
        show_thoughts = st.checkbox(":brain: Zobrazit myšlení agenta", value=True)
        
        st.divider()
        if "history" in st.session_state and st.session_state.history:
            transcript = "\n\n".join(f"{role.upper()}: {txt}" for role, txt in st.session_state.history)
            st.download_button("⬇️ Stáhnout přepis", transcript, "chat_přepis.txt", "text/plain")
    
    return show_thoughts


def render_chat_history():
    """Render the chat history from session state."""
    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize the session state for chat history."""
    if "history" not in st.session_state:
        st.session_state.history = []


def get_user_input() -> str:
    """Get user input from chat input or preset query.
    
    Returns:
        str: The user query or empty string if no input
    """
    primary_input = st.chat_input("Zadejte dotaz…", key="main_input")
    # A preset query (from quick button) overrides keyboard input for this turn
    return st.session_state.pop("preset_query", None) or primary_input 