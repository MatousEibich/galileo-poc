"""Streamlit chatbot – fixed quick‑prompt flow & continuous input
Creates a seamless UX: chat input is always on screen; quick‑prompt buttons
no longer hide it and conversation can proceed in the same rerun.
"""

import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler

from agent import get_agent
from ui_components import (
    setup_page_config, 
    render_sidebar, 
    render_chat_history,
    initialize_session_state,
    get_user_input
)


def process_user_query(agent, user_query: str, show_thoughts: bool):
    """Process a user query and generate a response."""
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.history.append(("user", user_query))

    # Generate assistant response
    with st.chat_message("assistant"):
        cb_container = st.container()
        cb_handler = StreamlitCallbackHandler(cb_container) if show_thoughts else None
        with st.spinner("Zpracovávám dotaz…"):
            answer = agent.run(user_query, callbacks=[cb_handler] if cb_handler else None)
        st.markdown(answer, unsafe_allow_html=True)
    st.session_state.history.append(("assistant", answer))


def main():
    """Main application function."""
    # Setup
    setup_page_config()
    initialize_session_state()
    
    # Create agent
    agent = get_agent()
    
    # UI Layout
    show_thoughts = render_sidebar()
    
    # Main chat area
    st.title("🗂️ Chatbot městských dat")
    
    # Get user input
    user_query = get_user_input()
    
    # Render chat history
    render_chat_history()
    
    # Process new query if provided
    if user_query:
        process_user_query(agent, user_query, show_thoughts)


if __name__ == "__main__":
    main()

