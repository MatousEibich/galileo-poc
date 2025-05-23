# Galileo POC

A modular Streamlit application using LangChain and OpenAI for querying Czech municipal data.

## Project Structure

- `app.py` - Main Streamlit application entry point
- `config.py` - Configuration settings and system prompts
- `agent.py` - LangChain agent setup and management
- `ui_components.py` - Streamlit UI helper functions
- `data/` - CSV files containing municipal data
- `prompts/` - System and agent prompts
- `agents/` - Agent factory and related components
- `eval/` - Evaluation framework for testing agent responses
- `static/` - Static assets (e.g., images, CSS)

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────┐     ┌───────────────┐     ┌───────────────┐
│  Streamlit  │     │   LangChain   │     │     OpenAI    │
│    UI       │────▶│    Agent      │────▶│     API       │
│             │     │               │     │               │
└─────────────┘     └───────────────┘     └───────────────┘
       ▲                    ▲                    ▲
       │                    │                    │
       │                    │                    │
┌──────┴────────┐   ┌──────┴────────┐    ┌──────┴────────┐
│  UI           │   │  Agent        │    │  Config &     │
│  Components   │   │  Factory      │    │  Prompts      │
└───────────────┘   └───────────────┘    └───────────────┘
                             ▲
                             │
                     ┌───────┴────────┐
                     │     CSV        │
                     │     Data       │
                     └────────────────┘
```

### Key Components:

1. **UI Layer** (`app.py`, `ui_components.py`):
   - Handles user interaction and chat interface
   - Manages session state and chat history
   - Provides quick prompt buttons and sidebar controls

2. **Agent Layer** (`agent.py`, `agents/factory.py`):
   - Creates and configures the LangChain CSV agent
   - Manages conversation memory
   - Processes user queries through the agent

3. **Configuration** (`config.py`, `prompts/system_prompt.txt`):
   - Centralized configuration settings
   - System prompts and templates
   - CSV data paths and LLM settings

4. **Evaluation Framework** (`eval/`):
   - Independent test framework for agent responses
   - Ground truth comparison using LLM-as-a-judge
   - Performance metrics and response quality assessment

## Setup

1. Make sure you have Python 3.12.4 or higher installed
2. Install Poetry if you don't have it already: https://python-poetry.org/docs/#installation
3. Clone this repository
4. Install dependencies:
```
poetry install
```

For evaluation functionality, use:
```
poetry install -E eval
```

## Environment Variables

Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

Locally:
```
poetry run python app.py
```

Or run with Streamlit:
```
poetry run streamlit run app.py
```

## Streamlit Cloud Deployment

This project can be deployed to Streamlit Cloud:

1. Push your repository to GitHub
2. Add your `OPENAI_API_KEY` to Streamlit Cloud secrets:
   - In Streamlit Cloud dashboard, go to your app settings
   - Navigate to "Secrets" section
   - Add your API key in the format:
   ```
   OPENAI_API_KEY = "your-api-key-here"
   ```
3. Deploy with the appropriate entry point (app.py)

The project is configured with `package-mode = false` in the pyproject.toml file to fix Poetry deployment issues on Streamlit Cloud.

## Required Dependencies

All dependencies are managed through `pyproject.toml`, which includes:
- langchain and related packages (langchain-openai, langchain-core, langchain-experimental)
- openai
- streamlit
- pandas
- tabulate
- python-dotenv
- jsonpath-ng

## Development

This project uses Poetry for dependency management and virtual environments. The virtual environment is configured to be created in the `.venv` directory within the project.

The codebase is organized into modular components for better maintainability:
- Configuration and prompts are centralized in `config.py`
- Agent logic is separated in `agent.py` 
- UI components are modularized in `ui_components.py`
- Main application flow is in `app.py` 