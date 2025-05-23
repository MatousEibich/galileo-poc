"""Run evaluation questions through the agent and collect responses.

This script is completely independent from the Streamlit UI and only evaluates
the agent's performance on predefined questions.
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from root
sys.path.append(str(Path(__file__).parent.parent))

# Import dependencies directly without streamlit
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

from config import CSV_FILES, MODEL_NAME, TEMPERATURE, get_system_prompt


def create_eval_agent():
    """Create CSV agent for evaluation (without streamlit caching)."""
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Fix CSV paths to work from eval subfolder
    eval_csv_files = [str(Path(__file__).parent.parent / path) for path in CSV_FILES]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        ("system", "Dosavadní konverzace:\n{chat_history}"),
        ("human", "{input}"),
    ])
    
    return create_csv_agent(
        ChatOpenAI(temperature=TEMPERATURE, model=MODEL_NAME),
        eval_csv_files,
        prompt=prompt,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        memory=memory,
    )


def run_evaluation(questions_file: str, output_file: str):
    """Run all evaluation questions through the agent and save results.
    
    Args:
        questions_file: Path to JSON file with evaluation questions
        output_file: Path to save agent responses
    """
    # Load questions
    print(f"Loading evaluation questions from {questions_file}")
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Initialize the agent
    print(f"Initializing agent with CSV files: {CSV_FILES}")
    agent = create_eval_agent()
    
    # Prepare results structure
    results = []
    total_questions = len(questions)
    
    print(f"Running {total_questions} evaluation questions...")
    print("-" * 60)
    
    # Process each question
    for i, question_data in enumerate(questions):
        question_id = question_data['id']
        question = question_data['question']
        expected_dataset = question_data.get('dataset', '')
        notes = question_data.get('notes', '')
        
        print(f"[{i+1}/{total_questions}] Question {question_id}: {question}")
        
        # Time the response
        start_time = time.time()
        try:
            response = agent.run(question)
            success = True
            error_msg = None
        except Exception as e:
            response = f"ERROR: {str(e)}"
            success = False
            error_msg = str(e)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Store result
        result = {
            "id": question_id,
            "question": question,
            "response": response,
            "expected_dataset": expected_dataset,
            "notes": notes,
            "duration": duration,
            "success": success,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result)
        
        if success:
            print(f"  ✓ Completed in {duration:.2f} seconds")
            # Print first 100 chars of response for quick review
            preview = response.replace('\n', ' ')[:100]
            print(f"  Preview: {preview}...")
        else:
            print(f"  ✗ Failed in {duration:.2f} seconds: {error_msg}")
        
        print()
    
    # Save results to JSON
    print(f"Saving results to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Print summary
    successful_runs = sum(1 for r in results if r['success'])
    failed_runs = total_questions - successful_runs
    avg_duration = sum(r['duration'] for r in results) / len(results)
    
    print("-" * 60)
    print("EVALUATION SUMMARY")
    print(f"Total questions: {total_questions}")
    print(f"Successful: {successful_runs}")
    print(f"Failed: {failed_runs}")
    print(f"Success rate: {(successful_runs/total_questions)*100:.1f}%")
    print(f"Average response time: {avg_duration:.2f} seconds")
    print(f"Results saved to: {output_file}")
    

def main():
    """Main function to run the evaluation."""
    # Setup paths
    questions_file = "eval_questions.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"eval_responses_{timestamp}.json"
    
    # Verify questions file exists
    if not Path(questions_file).exists():
        print(f"Error: Questions file '{questions_file}' not found!")
        print("Please create this file first with your evaluation questions.")
        return
    
    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Run the evaluation
    try:
        run_evaluation(questions_file, output_file)
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user.")
    except Exception as e:
        print(f"Error during evaluation: {e}")


if __name__ == "__main__":
    main() 