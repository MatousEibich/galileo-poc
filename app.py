"""Streamlit chatbot – fixed quick‑prompt flow & continuous input.

Creates a seamless UX: chat input is always on screen; quick‑prompt buttons
no longer hide it and conversation can proceed in the same rerun.
"""

import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler

from agent import get_agent
from ui_components import (
    get_user_input,
    initialize_session_state,
    render_chat_history,
    render_sidebar,
    setup_page_config,
)
from utils.exceptions import ConfigurationError
from utils.logging import get_logger, log_exception, setup_logging

# Setup logging
logger = get_logger(__name__)


def process_user_query(agent, user_query: str, show_thoughts: bool) -> None:
    """Process a user query and generate a response.

    Args:
        agent: The LangChain agent instance
        user_query: User's input query
        show_thoughts: Whether to display agent reasoning

    """
    logger.info(f"Processing user query: {user_query[:50]}...")

    try:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.history.append(("user", user_query))

        # Generate assistant response
        with st.chat_message("assistant"):
            cb_container = st.container()
            cb_handler = StreamlitCallbackHandler(cb_container) if show_thoughts else None

            try:
                with st.spinner("Zpracovávám dotaz…"):
                    answer = agent.run(user_query, callbacks=[cb_handler] if cb_handler else None)

                if not answer or not answer.strip():
                    logger.warning("Agent returned empty response")
                    answer = (
                        "Omlouvám se, ale nepodařilo se mi zpracovat váš dotaz. "
                        "Zkuste to prosím znovu."
                    )

                st.markdown(answer, unsafe_allow_html=True)
                st.session_state.history.append(("assistant", answer))

                logger.info("Query processed successfully")

            except Exception as e:
                log_exception(logger, e, "generating agent response")
                error_message = (
                    "Omlouvám se, ale došlo k chybě při zpracování vašeho dotazu. "
                    "Zkuste to prosím znovu."
                )
                st.error(error_message)
                st.session_state.history.append(("assistant", error_message))

    except Exception as e:
        log_exception(logger, e, "processing user query")
        st.error("Došlo k neočekávané chybě. Obnovte prosím stránku.")


@st.cache_resource(show_spinner=False)
def initialize_agent():
    """Initialize the agent with error handling.

    Returns:
        Agent instance or None if initialization fails

    """
    try:
        logger.info("Initializing agent...")
        agent = get_agent()
        logger.info("Agent initialized successfully")
        return agent
    except Exception as e:
        log_exception(logger, e, "initializing agent")
        return None


def main() -> None:
    """Run the main application."""
    try:
        # Setup logging for the application
        setup_logging(log_level="INFO", enable_console=True, enable_file=True)
        logger.info("Starting Galileo POC application")

        # Setup page configuration
        try:
            setup_page_config()
            logger.debug("Page configuration set up")
        except Exception as e:
            log_exception(logger, e, "setting up page configuration")
            st.error("Chyba při načítání konfigurace stránky")
            return

        # Initialize session state
        try:
            initialize_session_state()
            logger.debug("Session state initialized")
        except Exception as e:
            log_exception(logger, e, "initializing session state")
            st.error("Chyba při inicializaci relace")
            return

        # Create agent
        agent = initialize_agent()
        if agent is None:
            st.error("Nepodařilo se inicializovat chatbota. Zkontrolujte prosím konfiguraci.")
            logger.error("Failed to initialize agent, stopping application")
            return

        # UI Layout
        try:
            show_thoughts = render_sidebar()
            logger.debug("Sidebar rendered")
        except Exception as e:
            log_exception(logger, e, "rendering sidebar")
            st.error("Chyba při načítání postranního panelu")
            show_thoughts = True  # Default fallback

        # Main chat area
        st.title("🏙️ Chatbot městských dat Horšovský Týn")

        # Get user input
        try:
            user_query = get_user_input()
            logger.debug(f"User input received: {bool(user_query)}")
        except Exception as e:
            log_exception(logger, e, "getting user input")
            user_query = None

        # Render chat history
        try:
            render_chat_history()
            logger.debug("Chat history rendered")
        except Exception as e:
            log_exception(logger, e, "rendering chat history")
            st.warning("Chyba při zobrazování historie chatu")

        # Process new query if provided
        if user_query:
            process_user_query(agent, user_query, show_thoughts)

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        st.error(f"Chyba konfigurace: {e}")
    except Exception as e:
        log_exception(logger, e, "main application")
        st.error("Došlo k kritické chybě aplikace. Obnovte prosím stránku.")


if __name__ == "__main__":
    main()
