"""Shared agent factory for creating CSV agents across the application."""

import pandas as pd
from pathlib import Path
from typing import Any

from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI

from config import MODEL_NAME, TEMPERATURE, get_system_prompt, validate_csv_files
from utils.exceptions import AgentError, ValidationError
from utils.logging import get_logger, log_exception

# Setup logger
logger = get_logger(__name__)


def create_csv_chatbot_agent(
    csv_files: list[str],
    base_path: Path | None = None,
    use_memory: bool = True,
    model_name: str | None = None,
    temperature: float | None = None,
    verbose: bool = True,
) -> Any:
    """Create a CSV agent for the municipal data chatbot.

    Args:
        csv_files: List of CSV file paths
        base_path: Base path to resolve relative CSV paths (if None, uses current working directory)
        use_memory: Whether to use conversation memory
        model_name: OpenAI model name (defaults to config.MODEL_NAME)
        temperature: Model temperature (defaults to config.TEMPERATURE)
        verbose: Whether to enable verbose logging for the agent

    Returns:
        Configured CSV agent

    Raises:
        ValidationError: If input parameters are invalid
        AgentError: If agent creation fails

    """
    logger.info("Creating CSV chatbot agent")

    try:
        # Configure pandas display options for better LLM visibility
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', 20)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.expand_frame_repr', False)
        logger.debug("Configured pandas display options for optimal LLM visibility")

        # Validate inputs
        if not csv_files:
            raise ValidationError("csv_files cannot be empty")

        if temperature is not None and not (0.0 <= temperature <= 1.0):
            raise ValidationError(f"temperature must be between 0.0 and 1.0, got {temperature}")

        # Use defaults if not provided
        effective_model_name = model_name or MODEL_NAME
        effective_temperature = temperature if temperature is not None else TEMPERATURE

        logger.debug(f"Using model: {effective_model_name}, temperature: {effective_temperature}")

        # Validate and resolve CSV file paths
        validated_files = validate_csv_files(csv_files, base_path)
        resolved_csv_files = [str(path) for path in validated_files]

        logger.info(f"Validated {len(resolved_csv_files)} CSV files")

        # Create memory if requested
        memory = None
        if use_memory:
            try:
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                logger.debug("Created conversation memory")
            except Exception as e:
                log_exception(logger, e, "creating conversation memory")
                raise AgentError("Failed to create conversation memory") from e

        # Get system prompt
        try:
            system_prompt = get_system_prompt()
            logger.debug("Retrieved system prompt")
        except Exception as e:
            log_exception(logger, e, "getting system prompt")
            raise AgentError("Failed to load system prompt") from e

        # Create prompt template
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("system", "Dosavadní konverzace:\n{chat_history}"),
                    ("human", "{input}"),
                ]
            )
            logger.debug("Created prompt template")
        except Exception as e:
            log_exception(logger, e, "creating prompt template")
            raise AgentError("Failed to create prompt template") from e

        # Create LLM
        try:
            llm = ChatOpenAI(temperature=effective_temperature, model=effective_model_name)
            logger.debug(f"Created ChatOpenAI instance with model {effective_model_name}")
        except Exception as e:
            log_exception(logger, e, "creating ChatOpenAI instance")
            raise AgentError("Failed to create OpenAI client") from e

        # Create and return agent with enhanced parameters
        try:
            agent = create_csv_agent(
                llm,
                resolved_csv_files,
                prompt=prompt,
                verbose=verbose,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                memory=memory,
                # Enhanced data visibility parameters
                include_df_in_prompt=True,  # Ensure DataFrame context is shown
                number_of_head_rows=15,     # Show more data context (increased from default 5)
            )

            logger.info("Successfully created CSV chatbot agent with enhanced data visibility")
            return agent

        except Exception as e:
            log_exception(logger, e, "creating CSV agent")
            raise AgentError("Failed to create CSV agent") from e

    except Exception as e:
        if isinstance(e, ValidationError | AgentError):
            raise
        log_exception(logger, e, "creating CSV chatbot agent")
        raise AgentError("Unexpected error during agent creation") from e


def validate_agent_response(response: Any) -> str:
    """Validate and sanitize agent response.

    Args:
        response: Raw response from the agent

    Returns:
        Validated response string

    Raises:
        ValidationError: If response is invalid

    """
    try:
        if response is None:
            raise ValidationError("Agent response is None")

        if isinstance(response, str):
            response_str = response
        elif hasattr(response, "content"):
            response_str = response.content
        else:
            response_str = str(response)

        if not response_str.strip():
            raise ValidationError("Agent response is empty")

        logger.debug(f"Validated agent response ({len(response_str)} characters)")
        return response_str.strip()

    except Exception as e:
        log_exception(logger, e, "validating agent response")
        if isinstance(e, ValidationError):
            raise
        raise ValidationError("Failed to validate agent response") from e
