# Agents

This directory contains agent factory and related components for the municipal data chatbot.

## Files

- `__init__.py` - Package initialization file
- `factory.py` - Agent factory functions for creating LangChain agents

## Agent Factory

The agent factory provides a central place for creating LangChain agents with consistent configuration. This avoids code duplication between the main application and evaluation components.

### Key Features

- **Consistent configuration**: All agents use the same prompts and settings
- **Flexible paths**: Support for resolving CSV paths relative to different base directories
- **Memory management**: Optional conversation memory
- **Centralized setup**: Single place to update agent configuration

## Usage

### Main Application

```python
from agents.factory import create_csv_chatbot_agent
from config import CSV_FILES

# Create an agent for the main app
agent = create_csv_chatbot_agent(CSV_FILES)
```

### Evaluation System

```python
from agents.factory import create_csv_chatbot_agent
from config import CSV_FILES
from pathlib import Path

# Create an agent for evaluation with resolved paths
base_path = Path(__file__).parent.parent
agent = create_csv_chatbot_agent(CSV_FILES, base_path=base_path)
```

## Extending

To add new agent types or configurations:
1. Create new factory functions in `factory.py`
2. Expose them in `__init__.py`
3. Update consuming code to use the new factory functions 