# Prompts

This directory contains prompt templates used by the municipal data chatbot. These are separated from the code to make them easier to modify and maintain.

## Files

- `system_prompt.txt` - Main system prompt for the LangChain agent, describing the data structure and guidelines for responding to user queries.

## Prompt Structure

The system prompt includes:
1. Description of the agent's role and capabilities
2. Detailed schema of the CSV data files
3. Guidelines for processing and responding to queries
4. Rules for handling non-exact matches in the data
5. Time-sensitive considerations

## Usage

Prompts are loaded at runtime by the `get_system_prompt()` function in `config.py`. The prompt templates support variable substitution for dynamic content like the current date and time.

Example:
```python
prompt_template.format(current_time=CURRENT_TIME)
```

## Modifying Prompts

When modifying prompts:
1. Maintain all placeholders (e.g., `{current_time}`)
2. Test changes thoroughly to ensure the agent behaves as expected
3. Consider that changes to prompts can significantly impact agent behavior 