from typing import List, Dict
from ..utils import (
    extract_relevant_words,
    calculate_kendall_tau_distance,
    calculate_efficiency_modifier,
    format_percentage
)

def calculate_metrics(expected_outputs: List[str], model_predictions: List[str], prompt: str) -> Dict:
    """Calculate metrics for word sorting task."""
    if not expected_outputs or not model_predictions:
        return {
            'accuracy': 0,
            'word_accuracy': 0,
            'word_order_distance': 0,
            'combined_score': 0,
            'prompt_length': len(prompt),
            'efficiency_modifier': 0,
            'total_tests': 0,
            'correct_count': 0
        }

    # Process predictions and outputs
    processed_predictions = []
    processed_outputs = []
    for exp, pred in zip(expected_outputs, model_predictions):
        processed_pred = extract_relevant_words(pred, exp)
        processed_predictions.append(processed_pred)
        processed_outputs.append(exp.strip())
    
    # Calculate exact matches
    correct = sum(1 for exp, pred in zip(processed_outputs, processed_predictions) if exp == pred)
    accuracy = correct / len(processed_outputs) if processed_outputs else 0
    
    # Calculate word-level metrics
    total_words = 0
    correct_words = 0
    word_order_distances = []
    
    for exp, pred in zip(processed_outputs, processed_predictions):
        exp_words = exp.split()
        pred_words = pred.split()
        total_words += len(exp_words)
        correct_words += sum(1 for e, p in zip(exp_words, pred_words) if e == p)
        word_order_distances.append(calculate_kendall_tau_distance(exp_words, pred_words))
    
    word_accuracy = correct_words / total_words if total_words > 0 else 0
    avg_word_order_distance = sum(word_order_distances) / len(word_order_distances) if word_order_distances else 1

    # Calculate efficiency and combined score
    prompt_length = len(prompt)
    efficiency_modifier = calculate_efficiency_modifier(prompt_length, "word_sorting")
    
    accuracy_contribution = accuracy * 0.4
    word_accuracy_contribution = word_accuracy * 0.4
    distance_contribution = (1 - avg_word_order_distance) * 0.2
    
    base_combined_score = accuracy_contribution + word_accuracy_contribution + distance_contribution
    combined_score = base_combined_score * efficiency_modifier
    
    return {
        'accuracy': format_percentage(accuracy),
        'word_accuracy': format_percentage(word_accuracy),
        'word_order_distance': round(avg_word_order_distance, 2),
        'combined_score': format_percentage(combined_score),
        'prompt_length': prompt_length,
        'efficiency_modifier': efficiency_modifier,
        'total_tests': len(processed_outputs),
        'correct_count': correct
    }