# Evaluation Framework

This folder contains a complete evaluation framework for the municipal data chatbot with ground truth comparison and LLM-as-a-judge scoring.

## Folder Structure

```
eval/
├── questions/
│   ├── eval_questions_with_ground_truth.json  # Full question set (10 questions)
│   └── eval_questions_test.json               # Test subset (3 questions) 
├── results/
│   ├── responses/     # Agent response JSON files (eval_responses_*.json)
│   └── grades/        # LLM-as-judge grading results (eval_grades_*.json)  
├── eval_agent.py                              # Agent evaluation script
├── eval_grading.py                            # LLM-as-a-judge grading
└── README.md                                  # This file
```

## Files

### Core Evaluation Files
- **`questions/eval_questions_with_ground_truth.json`** - 10 evaluation questions with ground truth answers from actual data
- **`questions/eval_questions_test.json`** - 3-question subset for quick testing (saves tokens)
- **`eval_agent.py`** - Runs questions through the agent and collects responses
- **`eval_grading.py`** - LLM-as-a-judge grading with ground truth comparison

## Ground Truth Evaluation System

The evaluation system compares agent responses against factual ground truth answers extracted from the actual municipal data. This provides objective evaluation based on accuracy rather than subjective assessment.

### Question Structure
Each question includes:
- `id`: Unique question identifier
- `question`: Question in Czech
- `dataset`: Source dataset (editors_tyn, official_boards_tyn, messages_tyn)
- `ground_truth`: Correct answer extracted from actual data
- `notes`: Additional context about the question

### Example Question
```json
{
  "id": 1,
  "question": "Jakými kontakty můžu získat více informací o přidělování bytů v DPS?",
  "dataset": "editors_tyn",
  "ground_truth": "Pro získání více informací o přidělování bytů v DPS kontaktujte: Irena Kvítková, DiS. (pečovatelská služba), tel. 379 415 158, 730 132 142, e-mail: i.kvitkova@muht.cz. Pracovní doba: pondělí a středa 7:00 - 17:00, úterý a čtvrtek 7:00 - 15:00, pátek 7:00 - 13:30 hodin.",
  "notes": "Based on specific contact information in the apartment allocation page"
}
```

## Usage

### Quick Testing (Recommended)
For development and testing, use the 3-question subset to save time and tokens:

```bash
# Run 3-question test evaluation
python eval_agent.py --questions questions/eval_questions_test.json

# Grade the test results  
python eval_grading.py eval_responses_YYYYMMDD_HHMMSS.json --questions questions/eval_questions_test.json
```

### Full Evaluation
For comprehensive assessment, use the complete 10-question set:

```bash
# Run full evaluation
python eval_agent.py --questions questions/eval_questions_with_ground_truth.json

# Grade the full results
python eval_grading.py eval_responses_YYYYMMDD_HHMMSS.json --questions questions/eval_questions_with_ground_truth.json
```

### File Management
All results are automatically organized:
- **Agent responses** → `results/responses/eval_responses_YYYYMMDD_HHMMSS.json`
- **LLM grades** → `results/grades/eval_grades_with_ground_truth_YYYYMMDD_HHMMSS.json`

### Command Options
- `--questions` / `-q`: Specify questions file (default: questions/eval_questions_with_ground_truth.json)
- `--output` / `-o`: Specify output file (default: timestamped filename in appropriate results folder)

## Evaluation Criteria

The LLM-as-a-judge evaluates responses on a 1-5 scale across four criteria:

1. **Accuracy** (1-5): How factually correct is the response compared to ground truth?
2. **Completeness** (1-5): How thoroughly does it cover the information in ground truth?
3. **Relevance** (1-5): How well does it address the specific question asked?
4. **Clarity** (1-5): How clear and understandable is the response in Czech?

### Scoring Scale
- **5**: Excellent - Matches ground truth perfectly or provides equivalent/better information
- **4**: Good - Contains most ground truth information with minor gaps or additions
- **3**: Average - Contains some ground truth information but with notable gaps
- **2**: Poor - Contains little ground truth information or significant inaccuracies
- **1**: Very Poor - Mostly incorrect, irrelevant, or completely missing ground truth

## Test Subset Results

The 3-question test subset covers:

### Question Coverage
1. **Contact Information** (editors_tyn) - Tests structured data retrieval
2. **Official Notice** (official_boards_tyn) - Tests official board data access
3. **Budget Information** (editors_tyn) - Tests complex data discovery

### Recent Test Results (2025-05-23)
- **Average Score**: 3.58/5
- **Success Rate**: 100% (all questions answered)
- **Score Distribution**: 1 perfect (5/5), 1 good (4/5), 1 poor (1.75/5)
- **Response Time**: 4.44 seconds average

### Key Insights
- ✅ **Strong**: Contact info retrieval, structured data access
- ❌ **Weak**: Data discovery when information exists but requires search

## Dependencies

The evaluation system requires:
- LangChain for agent execution and LLM-as-judge
- OpenAI API access for GPT models
- Pandas for CSV data handling

Install with:
```bash
uv pip install -e ".[eval]"
```

## Benefits of Ground Truth Evaluation

1. **Objective Assessment**: Responses judged against factual data, not subjective opinion
2. **Specific Feedback**: Identifies exactly what information is missing or incorrect
3. **Data-Driven Improvement**: Highlights areas where the agent struggles with actual data
4. **Consistent Scoring**: Ground truth provides stable baseline for repeated evaluations
5. **Real-World Relevance**: Questions based on actual municipal data users would query
6. **Efficient Testing**: Small test subset enables rapid iteration during development

This framework enables systematic improvement of the chatbot's accuracy and completeness in handling municipal data queries. 