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
       
       # Build a generic evaluation prompt using the evaluation_guide
       evaluation_prompt = f"""Evaluate this solution for the given task.

Task Description:
{task_description}

User's Solution:
{user_output}

Reference Solution:
{reference_solution}

Evaluation criteria from the guide:
1. Format requirements: {evaluation_guide.get('format_requirements', {})}
2. Valid patterns: {evaluation_guide.get('valid_entries', {})}

Provide scores and feedback in exactly this format:
SCORE_RULES: [0-100] (Following core task rules and requirements)
SCORE_ACCURACY: [0-100] (Correctness of transformations and content)
SCORE_FORMAT: [0-100] (Proper formatting and structure)

FEEDBACK:
[Clear evaluation of:
- Each incorrect entry and why
- Format issues if any
- Specific improvements needed]"""

       logger.info(f"Sending evaluation request to GROQ for task: {task_description[:100]}...")
       logger.info(f"User output to evaluate: {user_output[:100]}...")

       chat_completion = client.chat.completions.create(
           messages=[{"role": "system", "content": "You are an evaluator for complex transformation tasks."}, 
                    {"role": "user", "content": evaluation_prompt}],
           model="llama3-70b-8192",
           temperature=0.1
       )

       raw_response = chat_completion.choices[0].message.content.strip()
       logger.info(f"Raw GROQ response: {raw_response}")

       scores = {'rules': 0, 'accuracy': 0, 'format': 0}
       feedback = ""
       in_feedback = False

       for line in raw_response.split('\n'):
           if line.startswith('SCORE_'):
               try:
                   category = line.split(':')[0].replace('SCORE_', '').lower()
                   score_text = line.split(':')[1].strip()
                   score = float(score_text.split()[0])
                   scores[category] = score
                   logger.info(f"Parsed score for {category}: {score}")
               except (ValueError, IndexError) as e:
                   logger.warning(f"Error parsing score line: {line}, {str(e)}")
                   continue
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
       logger.info(f"Calculated total score: {total_score}")

       return {
           "score": total_score,
           "explanation": feedback.strip(),
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
    inputs: List[Dict],
    prompt_lengths: List[int] = None  # Add this parameter
) -> Dict:
    logger.info(f"Starting complex metrics calculation with {len(task_descriptions)} tasks")
    logger.info(f"System prompt length: {len(system_prompt)}")
    logger.info(f"Prompt lengths received: {prompt_lengths}")
    
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

    # Calculate total prompt length
    total_prompt_length = sum(prompt_lengths) if prompt_lengths else len(system_prompt)
    logger.info(f"Total prompt length calculated: {total_prompt_length}")
    
    efficiency_modifier = calculate_efficiency_modifier(total_prompt_length, "complex_transformation")
    logger.info(f"Calculated efficiency modifier: {efficiency_modifier}")
    
    individual_scores = []
    total_rule_accuracy = 0.0
    total_completeness = 0.0
    total_format_score = 0.0
    total_score = 0.0
    
    for i, (task_desc, user_out, ref_sol) in enumerate(zip(
        task_descriptions, user_outputs, reference_solutions
    )):
        try:
            logger.info(f"Evaluating example {i + 1}")
            result = evaluate_with_groq(
                task_description=task_desc,
                user_output=user_out,
                reference_solution=ref_sol,
                evaluation_guide=inputs[i].get('evaluation_guide', {})
            )
            
            individual_score = result["score"] * 100  # Convert to percentage
            total_score += individual_score
            total_rule_accuracy += result["rule_accuracy"]
            total_completeness += result["completeness"]
            total_format_score += result["format_score"]
            
            individual_scores.append({
                'raw_score': round(individual_score, 2),
                'adjusted_score': round(individual_score * efficiency_modifier, 2),
                'explanation': result.get("explanation", ""),
                'rule_accuracy': result["rule_accuracy"],
                'completeness': result["completeness"],
                'format_score': result["format_score"]
            })
            logger.info(f"Example {i + 1} scores: {individual_scores[-1]}")
        except Exception as e:
            logger.error(f"Error evaluating example {i}: {str(e)}")
            individual_scores.append({
                'raw_score': 0.0,
                'adjusted_score': 0.0,
                'explanation': f"Error during evaluation: {str(e)}",
                'rule_accuracy': 0.0,
                'completeness': 0.0,
                'format_score': 0.0
            })

    num_examples = len(task_descriptions)
    if num_examples > 0:
        avg_rule_accuracy = total_rule_accuracy / num_examples
        avg_completeness = total_completeness / num_examples
        avg_format_score = total_format_score / num_examples
        avg_score = total_score / num_examples
    else:
        avg_rule_accuracy = avg_completeness = avg_format_score = avg_score = 0.0

    final_score = avg_score * efficiency_modifier

    result = {
        'final_score': round(final_score, 2),
        'efficiency': round(efficiency_modifier * 100, 2),
        'prompt_length': total_prompt_length,
        'total_tests': num_examples,
        'individual_scores': individual_scores,
        'rule_accuracy': round(avg_rule_accuracy, 1),
        'completeness': round(avg_completeness, 1),
        'format_score': round(avg_format_score, 1)
    }
    
    logger.info(f"Final results: {result}")
    return result