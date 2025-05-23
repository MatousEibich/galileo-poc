"""Agent setup and management for the municipal data chatbot."""

import streamlit as st
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

from config import CSV_FILES, MODEL_NAME, TEMPERATURE, get_system_prompt


def create_prompt() -> ChatPromptTemplate:
    """Create the chat prompt template."""
    return ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        ("system", "Dosavadní konverzace:\n{chat_history}"),
        ("human", "{input}"),
    ])


@st.cache_resource(show_spinner=False)
def get_agent():
    """Create and cache the CSV agent."""
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    prompt = create_prompt()
    
    return create_csv_agent(
        ChatOpenAI(temperature=TEMPERATURE, model=MODEL_NAME),
        CSV_FILES,
        prompt=prompt,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        memory=memory,
    ) 