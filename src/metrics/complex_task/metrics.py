from typing import Dict, Any, List
import os
import json
from groq import Groq
import logging
from ..utils import calculate_efficiency_modifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_with_groq(
    task_description: str,
    user_output: str,
    reference_solution: str,
    evaluation_guide: Dict
) -> Dict:
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY", "").strip())
        
        evaluation_prompt = f"""Evaluate this solution based on:

Task Description:
{task_description}

User's Solution:
{user_output}

Reference Solution:
{reference_solution}

Provide scores and feedback in exactly this format:
SCORE_RULES: [0-100] (Following core task rules and requirements)
SCORE_ACCURACY: [0-100] (Correctness of solution, including factual accuracy)
SCORE_FORMAT: [0-100] (Proper formatting, structure, and readability)

FEEDBACK:
[Clear explanation of:
- Rule adherence/violations
- Accuracy issues (including factual errors)
- Formatting and structure feedback]"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are an evaluator for complex transformation tasks."}, 
                     {"role": "user", "content": evaluation_prompt}],
            model="llama3-70b-8192",
            temperature=0.1
        )

        raw_response = chat_completion.choices[0].message.content.strip()
        logger.info(f"Raw GROQ response: {raw_response}")

        scores = {}
        feedback = ""
        in_feedback = False

        for line in raw_response.split('\n'):
            if line.startswith('SCORE_'):
                category = line.split(':')[0].replace('SCORE_', '').lower()
                score = float(line.split(':')[1].strip())
                scores[category] = score
            elif line.startswith('FEEDBACK:'):
                in_feedback = True
            elif in_feedback:
                feedback += line + "\n"

        weights = {
            "rules": 0.4,
            "accuracy": 0.4,
            "format": 0.2
        }

        total_score = sum(scores.get(k, 0) * v for k, v in weights.items()) / 100

        return {
            "score": total_score,
            "explanation": feedback.strip(),
            # Return raw scores - HTML will display with /40 and /20
            "rule_accuracy": round(scores.get('rules', 0), 1),
            "completeness": round(scores.get('accuracy', 0), 1), 
            "format_score": round(scores.get('format', 0), 1)
        }

    except Exception as e:
        logger.error(f"Error in GROQ evaluation: {str(e)}")
        logger.exception(e)
        return {
            "score": 0.0,
            "explanation": f"Error during evaluation: {str(e)}",
            "rule_accuracy": 0.0,
            "completeness": 0.0,
            "format_score": 0.0
        }

def calculate_complex_metrics(
    task_descriptions: List[str],
    user_outputs: List[str],
    reference_solutions: List[str],
    system_prompt: str,
    inputs: List[Dict]
) -> Dict:
    if not all([task_descriptions, user_outputs, reference_solutions, system_prompt, inputs]):
        logger.error("Missing required inputs for complex metrics")
        return {
            'final_score': 0.0,
            'efficiency': 0.0,
            'prompt_length': len(system_prompt) if system_prompt else 0,
            'total_tests': 0,
            'individual_scores': [],
            'rule_accuracy': 0.0,
            'completeness': 0.0,
            'format_score': 0.0
        }

    if not (len(task_descriptions) == len(user_outputs) == len(reference_solutions) == len(inputs)):
        logger.error("Mismatched input lengths")
        return {
            'final_score': 0.0,
            'efficiency': 0.0,
            'prompt_length': len(system_prompt),
            'total_tests': 0,
            'individual_scores': [],
            'rule_accuracy': 0.0,
            'completeness': 0.0,
            'format_score': 0.0
        }

    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "complex_transformation")
    
    individual_scores = []
    total_score = 0.0
    
    for i, (task_desc, user_out, ref_sol) in enumerate(zip(
        task_descriptions, user_outputs, reference_solutions
    )):
        result = evaluate_with_groq(
            task_description=task_desc,
            user_output=user_out,
            reference_solution=ref_sol,
            evaluation_guide=inputs[i]['evaluation_guide']
        )
        
        individual_score = result["score"] * 100  # Convert to percentage
        total_score += result["score"]
        
        individual_scores.append({
            'raw_score': round(individual_score, 2),
            'adjusted_score': round(individual_score * efficiency_modifier, 2),
            'explanation': result.get("explanation", ""),
            'rule_accuracy': result["rule_accuracy"],
            'completeness': result["completeness"],
            'format_score': result["format_score"]
        })

    num_examples = len(task_descriptions)
    average_score = (total_score / num_examples) * 100
    final_score = average_score * efficiency_modifier

    first_score = individual_scores[0] if individual_scores else {
        'rule_accuracy': 0.0,
        'completeness': 0.0, 
        'format_score': 0.0,
        'explanation': ''
    }

    return {
        'final_score': round(final_score, 2),
        'efficiency': round(efficiency_modifier * 100, 2),
        'prompt_length': len(system_prompt),
        'total_tests': num_examples,
        'individual_scores': individual_scores,
        'rule_accuracy': first_score['rule_accuracy'],
        'completeness': first_score['completeness'], 
        'format_score': first_score['format_score']
    }