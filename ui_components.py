"""UI components for the municipal data chatbot."""

import streamlit as st
from typing import Tuple, List
from config import APP_TITLE, APP_ICON, LOGO_PATH
from utils.logging import get_logger, log_exception

# Setup logger
logger = get_logger(__name__)


def setup_page_config() -> None:
    """Configure the Streamlit page settings."""
    try:
        st.set_page_config(
            page_title=APP_TITLE, 
            page_icon=APP_ICON, 
            layout="wide"
        )
        logger.debug("Page configuration set successfully")
    except Exception as e:
        log_exception(logger, e, "setting up page configuration")
        raise


def render_sidebar() -> bool:
    """Render the sidebar with logo, quick buttons, and options.
    
    Returns:
        bool: Whether to show agent thoughts
    """
    try:
        with st.sidebar:
            # Display logo if it exists
            try:
                st.image(LOGO_PATH, width=160, caption="Město Horšovský Týn")
                logger.debug("Logo displayed successfully")
            except Exception as e:
                logger.warning(f"Could not display logo: {e}")
                # Continue without logo
            
            st.markdown("##### Chatbot městských dat")
            st.divider()

            st.markdown("**Rychlé dotazy:**")
            if st.button(":building_construction: Úřední deska"):
                st.session_state["preset_query"] = "Co je aktuálně na úřední desce?"
                logger.debug("Preset query set: úřední deska")
                
            if st.button(":houses: Bytové informace"):
                st.session_state["preset_query"] = "Jak funguje přidělování bytů v majetku města?"
                logger.debug("Preset query set: bytové informace")
                
            if st.button(":euro: Dotace z EU"):
                st.session_state["preset_query"] = "Jaké projekty jsou financovány z EU?"
                logger.debug("Preset query set: dotace z EU")

            st.divider()
            show_thoughts = st.checkbox(":brain: Zobrazit myšlení agenta", value=True)
            
            st.divider()
            if "history" in st.session_state and st.session_state.history:
                try:
                    transcript = "\n\n".join(
                        f"{role.upper()}: {txt}" for role, txt in st.session_state.history
                    )
                    st.download_button(
                        "⬇️ Stáhnout přepis", 
                        transcript, 
                        "chat_přepis.txt", 
                        "text/plain"
                    )
                    logger.debug("Download transcript button displayed")
                except Exception as e:
                    logger.warning(f"Could not create download button: {e}")
        
        return show_thoughts
        
    except Exception as e:
        log_exception(logger, e, "rendering sidebar")
        # Return default value on error
        return True


def render_chat_history() -> None:
    """Render the chat history from session state."""
    try:
        if "history" not in st.session_state:
            logger.debug("No chat history to render")
            return
            
        for role, message in st.session_state.history:
            with st.chat_message(role):
                st.markdown(message, unsafe_allow_html=True)
        
        logger.debug(f"Rendered {len(st.session_state.history)} chat messages")
        
    except Exception as e:
        log_exception(logger, e, "rendering chat history")
        st.warning("Chyba při zobrazování historie chatu")


def initialize_session_state() -> None:
    """Initialize the session state for chat history."""
    try:
        if "history" not in st.session_state:
            st.session_state.history = []
            logger.debug("Initialized empty chat history")
        else:
            logger.debug(f"Chat history already exists with {len(st.session_state.history)} messages")
            
    except Exception as e:
        log_exception(logger, e, "initializing session state")
        # Ensure we have a fallback
        st.session_state.history = []


def get_user_input() -> str:
    """Get user input from chat input or preset query.
    
    Returns:
        str: The user query or empty string if no input
    """
    try:
        primary_input = st.chat_input("Zadejte dotaz…", key="main_input")
        # A preset query (from quick button) overrides keyboard input for this turn
        user_query = st.session_state.pop("preset_query", None) or primary_input
        
        if user_query:
            logger.debug(f"User input received: {len(user_query)} characters")
        
        return user_query or ""
        
    except Exception as e:
        log_exception(logger, e, "getting user input")
        return "" 