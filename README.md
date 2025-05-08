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

```
poetry run python app.py
```

## Development

This project uses Poetry for dependency management and virtual environments. The virtual environment is configured to be created in the `.venv` directory within the project. 