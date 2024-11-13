from typing import List, Dict
from ..utils import calculate_efficiency_modifier, format_percentage

def standardize_causal_answer(answer: str) -> str:
    """Standardize causal judgment answers to 'Yes' or 'No'."""
    # Convert to lowercase and clean up whitespace
    clean_answer = answer.strip().lower()
    
    # Common phrases to remove
    phrases_to_remove = [
        "the answer is",
        "i think",
        "i believe",
        "therefore",
        "thus",
        "so",
        "based on this",
        "in this case",
        "in my opinion",
        "it appears that",
        "it seems that",
        "clearly",
        "obviously"
    ]
    
    # Remove common phrases and punctuation
    for phrase in phrases_to_remove:
        clean_answer = clean_answer.replace(phrase, "")
    clean_answer = clean_answer.replace('.', '').replace('!', '').replace(',', '').replace(':', '')
    
    # Clean up extra whitespace
    clean_answer = " ".join(clean_answer.split())
    
    # Look for yes/no
    if 'yes' in clean_answer.split():
        return 'Yes'
    if 'no' in clean_answer.split():
        return 'No'
    
    # Check for other affirmative/negative expressions
    affirmative = ['correct', 'true', 'right', 'indeed', 'affirmative', 'absolutely']
    negative = ['incorrect', 'false', 'wrong', 'negative', 'nope', 'nah']
    
    for word in clean_answer.split():
        if word in affirmative:
            return 'Yes'
        if word in negative:
            return 'No'
    
    return clean_answer

def is_valid_causal_answer(answer: str) -> bool:
    """Check if answer is a clear yes/no response."""
    clean = answer.strip().lower()
    if clean in ['yes', 'no']:
        return True
    if clean in ['yes.', 'no.', 'yes!', 'no!']:
        return True
    return False

def calculate_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    """Calculate metrics for causal judgment task."""
    # Standardize outputs and predictions
    standardized_expected = [exp.strip() for exp in expected_outputs]
    standardized_predictions = [standardize_causal_answer(pred) for pred in model_predictions]
    
    # Calculate base accuracy
    correct_count = sum(1 for exp, pred in zip(standardized_expected, standardized_predictions) 
                       if exp == pred)
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests) if total_tests > 0 else 0
    
    # Calculate format bonus for clear yes/no answers
    format_bonus = sum(1 for pred in standardized_predictions if pred in ['Yes', 'No'])
    
    # Calculate efficiency modifier and final accuracy
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "causal_judgement")
    final_accuracy = min(100, base_accuracy * efficiency_modifier)
    
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