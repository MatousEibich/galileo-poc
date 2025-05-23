# Evaluation System

This folder contains the complete evaluation framework for the Horšovský Týn municipal data chatbot.

## Files

### Core Scripts
- **`eval_agent.py`** - Main evaluation script that runs questions through the agent
- **`eval_grading.py`** - Placeholder for future LLM-as-a-judge grading system
- **`eval_questions.json`** - Set of evaluation questions covering all datasets

### Generated Files (gitignored)
- **`eval_responses_*.json`** - Timestamped agent responses
- **`eval_grades_*.json`** - Future grading results
- **`EVALUATION_RESULTS.md`** - Human-readable summary

## Usage

### Phase 1: Run Evaluation
```bash
# Activate the main project environment
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # Linux/Mac

cd eval
python eval_agent.py
```

### Phase 2: View Results
Check the generated `eval_responses_*.json` and `EVALUATION_RESULTS.md` files.

### Phase 3: Grade Responses (Future)
```bash
python eval_grading.py eval_responses_TIMESTAMP.json
```

## Dependencies

Uses the main project `.venv` environment with the "eval" optional dependency group:
```bash
uv pip install -e .[eval]
```

Or install eval dependencies directly:
```bash
uv pip install langchain langchain-openai langchain-core langchain-experimental openai python-dotenv pandas tabulate
```

## Environment

- Runs independently from the Streamlit app using the same `.venv`
- Uses the same CSV data files from `data/data-v2/`
- Requires OpenAI API key in environment
- Consolidated with main project environment - no separate eval environment needed 