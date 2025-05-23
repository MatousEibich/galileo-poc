# Galileo POC

A modular Streamlit application using LangChain and OpenAI for querying Czech municipal data.

## Project Structure

- `app.py` - Main Streamlit application entry point
- `config.py` - Configuration settings and system prompts
- `agent.py` - LangChain agent setup and management
- `ui_components.py` - Streamlit UI helper functions
- `data/` - CSV files containing municipal data
- `questions.txt` - Example questions for testing

## Setup

1. Make sure you have Python 3.12.4 or higher installed
2. Install Poetry if you don't have it already: https://python-poetry.org/docs/#installation
3. Clone this repository
4. Install dependencies:
```
poetry install
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

This project requires the following key dependencies:
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