"""Grade agent responses using LLM evaluation (LLM-as-a-judge) with ground truth comparison.

This script evaluates agent responses using an LLM to grade quality,
accuracy, and relevance by comparing against ground truth answers.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from root
sys.path.append(str(Path(__file__).parent.parent))

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import MODEL_NAME


def create_grading_prompt():
    """Create the LLM-as-a-judge prompt template with ground truth comparison."""
    # Read prompt from external file
    prompt_file = Path(__file__).parent / "prompts" / "llm_judge_prompt.txt"
    with open(prompt_file, encoding="utf-8") as f:
        prompt_template = f.read()

    return ChatPromptTemplate.from_template(prompt_template)


def load_questions_with_ground_truth(questions_file: str) -> dict:
    """Load evaluation questions with ground truth answers.

    Args:
        questions_file: Path to JSON file with questions and ground truth

    Returns:
        Dictionary mapping question ID to question data

    """
    print(f"Loading questions with ground truth from {questions_file}")
    with open(questions_file, encoding="utf-8") as f:
        questions = json.load(f)

    # Convert to dict for easy lookup
    questions_dict = {q["id"]: q for q in questions}
    print(f"Loaded {len(questions_dict)} questions with ground truth")
    return questions_dict


def grade_single_response(llm, prompt_template, response_data, ground_truth_data):
    """Grade a single response using the LLM judge with ground truth comparison."""
    try:
        # Format the prompt with response data and ground truth
        formatted_prompt = prompt_template.format(
            question=response_data["question"],
            ground_truth=ground_truth_data["ground_truth"],
            response=response_data["response"],
            expected_dataset=ground_truth_data.get("dataset", ""),
            notes=ground_truth_data.get("notes", ""),
        )

        # Get LLM evaluation
        result = llm.invoke(formatted_prompt)

        # Parse the JSON response
        grade_data = json.loads(result.content.strip())

        # Validate the required fields
        required_fields = ["accuracy", "completeness", "relevance", "clarity", "overall_score"]
        for field in required_fields:
            if field not in grade_data:
                raise ValueError(f"Missing required field: {field}")

        return grade_data, None

    except json.JSONDecodeError as e:
        return None, f"Failed to parse LLM response as JSON: {e}"
    except Exception as e:
        return None, f"Error during grading: {e}"


def load_responses(responses_file: str) -> list:
    """Load agent responses from JSON file.

    Args:
        responses_file: Path to JSON file with agent responses

    Returns:
        List of response data

    """
    print(f"Loading responses from {responses_file}")
    with open(responses_file, encoding="utf-8") as f:
        responses = json.load(f)
    return responses


def grade_responses(responses: list, questions_dict: dict) -> list:
    """Grade responses using LLM-as-a-judge approach with ground truth comparison.

    Args:
        responses: List of response data
        questions_dict: Dictionary of questions with ground truth

    Returns:
        List of graded responses

    """
    print(
        f"Grading {len(responses)} responses using LLM-as-a-judge with ground truth comparison..."
    )

    # Initialize LLM and prompt
    llm = ChatOpenAI(temperature=0.1, model=MODEL_NAME)  # Low temperature for consistent grading
    prompt_template = create_grading_prompt()

    graded_responses = []
    successful_grades = 0
    failed_grades = 0

    for i, response in enumerate(responses):
        print(
            f"[{i + 1}/{len(responses)}] Grading question {response['id']}: "
            f"{response['question'][:50]}..."
        )

        if not response.get("success", False):
            # Skip failed responses
            graded_response = response.copy()
            graded_response.update(
                {
                    "grade": None,
                    "grading_criteria": {
                        "accuracy": None,
                        "completeness": None,
                        "relevance": None,
                        "clarity": None,
                    },
                    "overall_score": None,
                    "grading_reasoning": "Original response failed - no grading performed",
                    "grading_error": None,
                    "graded_at": datetime.now().isoformat(),
                }
            )
            graded_responses.append(graded_response)
            continue

        # Find corresponding ground truth
        question_id = response["id"]
        if question_id not in questions_dict:
            graded_response = response.copy()
            graded_response.update(
                {
                    "grade": None,
                    "grading_criteria": {
                        "accuracy": None,
                        "completeness": None,
                        "relevance": None,
                        "clarity": None,
                    },
                    "overall_score": None,
                    "grading_reasoning": None,
                    "grading_error": f"No ground truth found for question ID {question_id}",
                    "graded_at": datetime.now().isoformat(),
                }
            )
            graded_responses.append(graded_response)
            failed_grades += 1
            print(f"  ✗ No ground truth found for question ID {question_id}")
            continue

        ground_truth_data = questions_dict[question_id]

        # Grade the response
        grade_data, error = grade_single_response(llm, prompt_template, response, ground_truth_data)

        # Create graded response
        graded_response = response.copy()

        if grade_data:
            graded_response.update(
                {
                    "grade": grade_data,
                    "grading_criteria": {
                        "accuracy": grade_data.get("accuracy"),
                        "completeness": grade_data.get("completeness"),
                        "relevance": grade_data.get("relevance"),
                        "clarity": grade_data.get("clarity"),
                    },
                    "overall_score": grade_data.get("overall_score"),
                    "grading_reasoning": grade_data.get("reasoning"),
                    "grading_strengths": grade_data.get("strengths"),
                    "grading_weaknesses": grade_data.get("weaknesses"),
                    "ground_truth": ground_truth_data["ground_truth"],
                    "grading_error": None,
                    "graded_at": datetime.now().isoformat(),
                }
            )
            successful_grades += 1
            print(f"  ✓ Graded (Overall: {grade_data.get('overall_score', 'N/A')}/5)")
        else:
            graded_response.update(
                {
                    "grade": None,
                    "grading_criteria": {
                        "accuracy": None,
                        "completeness": None,
                        "relevance": None,
                        "clarity": None,
                    },
                    "overall_score": None,
                    "grading_reasoning": None,
                    "ground_truth": ground_truth_data["ground_truth"],
                    "grading_error": error,
                    "graded_at": datetime.now().isoformat(),
                }
            )
            failed_grades += 1
            print(f"  ✗ Failed: {error}")

        graded_responses.append(graded_response)

    print(f"\nGrading complete: {successful_grades} successful, {failed_grades} failed")
    return graded_responses


def save_grades(graded_responses: list, output_file: str):
    """Save graded responses to JSON file.

    Args:
        graded_responses: List of graded response data
        output_file: Path to save graded results

    """
    print(f"Saving graded results to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graded_responses, f, ensure_ascii=False, indent=2)


def print_summary(graded_responses: list):
    """Print a summary of grading results."""
    successful_grades = [r for r in graded_responses if r.get("overall_score") is not None]
    failed_grades = [r for r in graded_responses if r.get("grading_error") is not None]
    skipped_grades = [r for r in graded_responses if not r.get("success", False)]

    print("-" * 60)
    print("GRADING SUMMARY")
    print(f"Total responses: {len(graded_responses)}")
    print(f"Successfully graded: {len(successful_grades)}")
    print(f"Failed to grade: {len(failed_grades)}")
    print(f"Skipped (original failures): {len(skipped_grades)}")

    if successful_grades:
        scores = [r["overall_score"] for r in successful_grades]
        avg_score = sum(scores) / len(scores)
        print(f"Average overall score: {avg_score:.2f}/5")

        # Score distribution
        score_dist = {}
        for score in scores:
            rounded_score = round(score)
            score_dist[rounded_score] = score_dist.get(rounded_score, 0) + 1

        print("Score distribution:")
        for score in sorted(score_dist.keys()):
            print(f"  {score}/5: {score_dist[score]} responses")


def main():
    """Grade agent responses."""
    parser = argparse.ArgumentParser(
        description="Grade agent responses using LLM-as-a-judge with ground truth"
    )
    parser.add_argument("responses_file", help="JSON file with agent responses")
    parser.add_argument(
        "--questions",
        "-q",
        default="eval_questions_with_ground_truth.json",
        help=(
            "JSON file with questions and ground truth "
            "(default: eval_questions_with_ground_truth.json)"
        ),
    )
    parser.add_argument("--output", "-o", default=None, help="Output file for grades")

    args = parser.parse_args()

    # Verify input files exist
    responses_file_path = Path(args.responses_file)
    if not responses_file_path.exists():
        # Try in results/responses/ if relative path doesn't exist
        alt_path = Path(__file__).parent / "results" / "responses" / args.responses_file
        if alt_path.exists():
            responses_file_path = alt_path
        else:
            print(f"Error: Responses file '{args.responses_file}' not found!")
            print(f"Tried: {responses_file_path}")
            print(f"Tried: {alt_path}")
            return

    questions_file = Path(__file__).parent / "questions" / args.questions
    if not questions_file.exists():
        print(f"Error: Questions file '{questions_file}' not found!")
        return

    # Set default output filename if not provided
    if args.output is None:
        responses_path = Path(args.responses_file)
        timestamp = responses_path.stem.replace("eval_responses_", "")
        output_file = (
            Path(__file__).parent
            / "results"
            / "grades"
            / f"eval_grades_with_ground_truth_{timestamp}.json"
        )
    else:
        output_file = Path(args.output)

    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Load questions with ground truth
        questions_dict = load_questions_with_ground_truth(str(questions_file))

        # Load responses
        responses = load_responses(str(responses_file_path))

        # Grade responses using LLM-as-a-judge with ground truth
        graded_responses = grade_responses(responses, questions_dict)

        # Save grades
        save_grades(graded_responses, str(output_file))

        # Print summary
        print_summary(graded_responses)

        print(f"\nResults saved to: {output_file}")

    except Exception as e:
        print(f"Error during grading: {e}")


if __name__ == "__main__":
    main()
