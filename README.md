# Galileo POC

A simple proof of concept using LangChain and OpenAI.

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
poetry run streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment

This project can be deployed to Streamlit Cloud:

1. Push your repository to GitHub
2. Add your `OPENAI_API_KEY` to Streamlit Cloud secrets
3. Deploy with `streamlit_app.py` as the entry point

The project is configured with `package-mode = false` in the pyproject.toml file to fix Poetry deployment issues on Streamlit Cloud.

## Development

This project uses Poetry for dependency management and virtual environments. The virtual environment is configured to be created in the `.venv` directory within the project. 