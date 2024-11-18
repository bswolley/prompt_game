import re
from ..utils import calculate_efficiency_modifier, format_percentage
from typing import List, Dict

def standardize_logical_answer(answer: str) -> str:
    """
    Standardize logical deduction answers to format (X) where X is a single letter A-G.
    """
    # Convert to uppercase and clean up whitespace
    clean_answer = answer.strip().upper()
    
    # Common phrases to remove
    phrases_to_remove = [
        "THE ANSWER IS",
        "THE CORRECT ANSWER IS",
        "ANSWER:",
        "THEREFORE,",
        "THUS,",
        "SO,",
        "IS CORRECT",
        "MUST BE",
        "SHOULD BE",
        "WOULD BE",
        "HAS TO BE"
    ]
    
    # Remove common phrases
    for phrase in phrases_to_remove:
        clean_answer = clean_answer.replace(phrase, "")
    
    # Clean up extra whitespace
    clean_answer = " ".join(clean_answer.split())
    
    # First try to find a letter within parentheses
    paren_match = re.search(r'\(([A-G])\)', clean_answer)
    if paren_match:
        return f"({paren_match.group(1)})"
    
    # Look for any single letter A-G
    letter_matches = re.findall(r'(?:^|\s)([A-G])(?:\s|$|\.|\,|\:|\)|\()', clean_answer)
    if letter_matches:
        return f"({letter_matches[0]})"
    
    # Last resort: just look for any A-G
    any_letter = re.search(r'[A-G]', clean_answer)
    if any_letter:
        return f"({any_letter.group(0)})"
    
    return clean_answer

def is_properly_formatted(answer: str) -> bool:
    """Check if answer is in proper format: '(A)' for any letter A-G."""
    clean = answer.strip().upper()
    if clean in ['(A)', '(B)', '(C)', '(D)', '(E)', '(F)', '(G)']:
        return True
    return False

def calculate_logical_deduction_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    individual_scores = []
    all_correct = []
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "logical_deduction")
    standardized_predictions = [standardize_logical_answer(pred) for pred in model_predictions]
    
    # Calculate individual scores FIRST
    for exp, std_pred in zip(expected_outputs, standardized_predictions):
        is_correct = exp.strip().upper() == std_pred.strip().upper()
        all_correct.append(is_correct)
        
        # Calculate THIS example's scores
        example_base_accuracy = 100 if is_correct else 0
        example_final_score = example_base_accuracy * efficiency_modifier
        
        individual_scores.append({
            'final_score': format_percentage(example_final_score),
            'base_accuracy': format_percentage(example_base_accuracy),
            'efficiency': format_percentage(efficiency_modifier * 100),
            'is_correct': is_correct
        })

    # Calculate overall metrics from stored results
    total_tests = len(expected_outputs)
    correct_count = sum(all_correct)
    base_accuracy = (correct_count / total_tests * 100) if total_tests > 0 else 0
    final_score = base_accuracy * efficiency_modifier

    return {
        'final_score': format_percentage(final_score),
        'accuracy': format_percentage(base_accuracy),
        'base_accuracy': format_percentage(base_accuracy),
        'efficiency': format_percentage(efficiency_modifier * 100),
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'individual_scores': individual_scores,
        'standardized_outputs': standardized_predictions
    }