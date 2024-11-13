from typing import List, Dict
import re
from ..utils import calculate_efficiency_modifier, format_percentage

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
    """Check if answer is in proper format: 'A' or '(A)' for any letter A-G."""
    clean = answer.strip().upper()
    if clean in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return True
    if clean in ['(A)', '(B)', '(C)', '(D)', '(E)', '(F)', '(G)']:
        return True
    return False

def calculate_logical_deduction_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    """Calculate metrics for logical deduction task."""
    # Standardize outputs and predictions
    standardized_expected = [standardize_logical_answer(exp) for exp in expected_outputs]
    standardized_predictions = [standardize_logical_answer(pred) for pred in model_predictions]
    
    # Calculate base accuracy
    correct_count = sum(1 for exp, pred in zip(standardized_expected, standardized_predictions) 
                       if exp == pred)
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests) if total_tests > 0 else 0
    
    # Calculate format bonus
    format_bonus = sum(1 for pred, std_pred, exp in 
                      zip(model_predictions, standardized_predictions, standardized_expected) 
                      if is_properly_formatted(pred) and std_pred == exp)
    
    # Calculate efficiency modifier and final accuracy
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "logical_deduction")
    efficiency_adjusted_accuracy = base_accuracy * efficiency_modifier
    final_accuracy = min(100, efficiency_adjusted_accuracy)
    
    return {
        'accuracy': format_percentage(final_accuracy),
        'base_accuracy': format_percentage(base_accuracy),
        'format_bonus': format_bonus,
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': standardized_predictions
    }