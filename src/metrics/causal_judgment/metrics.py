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

def calculate_causal_judgment_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    """Calculate metrics for causal judgment task."""
    # Standardize outputs and predictions
    standardized_expected = [exp.strip() for exp in expected_outputs]
    standardized_predictions = [standardize_causal_answer(pred) for pred in model_predictions]
    
    # Calculate efficiency modifier
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "causal_judgement")
    efficiency_percentage = efficiency_modifier * 100
    
    # Calculate individual scores FIRST
    individual_scores = []
    correct_count = 0
    
    for exp, pred in zip(standardized_expected, standardized_predictions):
        is_correct = exp.strip().lower() == pred.strip().lower()
        if is_correct:
            correct_count += 1
            
        # Calculate per-example metrics
        example_base_accuracy = 100 if is_correct else 0
        example_final_score = example_base_accuracy * efficiency_modifier
        
        individual_scores.append({
            'final_score': round(example_final_score, 2),  # Changed from format_percentage
            'base_accuracy': round(example_base_accuracy, 2),  # Changed from format_percentage
            'efficiency': round(efficiency_percentage, 2),  # Changed from format_percentage
            'is_correct': is_correct
        })
    
    # Calculate overall metrics
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests * 100) if total_tests > 0 else 0
    final_score = base_accuracy * efficiency_modifier

    return {
        'final_score': round(final_score, 2),  # Changed from format_percentage
        'accuracy': round(base_accuracy, 2),  # Changed from format_percentage
        'base_accuracy': round(base_accuracy, 2),  # Changed from format_percentage
        'efficiency': round(efficiency_percentage, 2),  # Changed from format_percentage
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': standardized_predictions,
        'individual_scores': individual_scores
    }