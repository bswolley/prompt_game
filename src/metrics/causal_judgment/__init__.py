from .metrics import calculate_causal_judgment_metrics
from typing import List, Dict
from ..utils import (
    calculate_efficiency_modifier,
    format_percentage
)

def standardize_causal_answer(answer: str) -> str:
    """Standardize causal judgment answers to 'Yes' or 'No'."""
    # Your existing standardize_causal_answer function code here

def calculate_causal_judgment_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    """Calculate metrics for causal judgment task."""
    # Standardize outputs and predictions
    standardized_expected = [exp.strip() for exp in expected_outputs]
    standardized_predictions = [standardize_causal_answer(pred) for pred in model_predictions]
    
    # Calculate efficiency modifier
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "causal_judgement")
    efficiency_percentage = efficiency_modifier * 100
    
    # Calculate individual scores
    individual_scores = []
    correct_count = 0
    
    for exp, pred in zip(standardized_expected, standardized_predictions):
        is_correct = exp.strip().lower() == pred.strip().lower()
        if is_correct:
            correct_count += 1
            
        example_accuracy = 100 if is_correct else 0
        example_score = example_accuracy * efficiency_modifier
        
        individual_scores.append({
            'final_score': format_percentage(example_score),
            'base_accuracy': format_percentage(example_accuracy),
            'efficiency': format_percentage(efficiency_percentage)
        })
    
    # Calculate overall metrics
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests * 100) if total_tests > 0 else 0
    final_score = base_accuracy * efficiency_modifier
    
    return {
        'final_score': format_percentage(final_score),
        'accuracy': format_percentage(base_accuracy),
        'base_accuracy': format_percentage(base_accuracy),
        'efficiency': format_percentage(efficiency_percentage),
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': standardized_predictions,
        'individual_scores': individual_scores
    }