from typing import List, Dict
from ..utils import (
    extract_relevant_words,
    calculate_kendall_tau_distance,
    calculate_efficiency_modifier,
    format_percentage
)

def calculate_word_sorting_metrics(expected_outputs: List[str], model_predictions: List[str], prompt: str) -> Dict:
    individual_scores = []
    all_exact_matches = []
    all_word_accuracies = []
    all_order_distances = []

    # Calculate individual scores FIRST
    for exp, pred in zip(expected_outputs, model_predictions):
        processed_pred = extract_relevant_words(pred, exp)
        exp_words = exp.strip().split()
        pred_words = processed_pred.split()
        
        # Per-example calculations
        is_exact_match = exp.strip() == processed_pred
        example_word_matches = sum(1 for e, p in zip(exp_words, pred_words) if e == p)
        example_word_accuracy = example_word_matches / len(exp_words) if exp_words else 0
        example_order_distance = calculate_kendall_tau_distance(exp_words, pred_words)
        
        # Store metrics for overall calculation
        all_exact_matches.append(is_exact_match)
        all_word_accuracies.append(example_word_accuracy)
        all_order_distances.append(example_order_distance)
        
        # Calculate THIS example's score
        example_score = (
            (0.4 * (100 if is_exact_match else 0)) +
            (0.4 * example_word_accuracy * 100) +
            (0.2 * (1 - example_order_distance) * 100)
        )
        
        individual_scores.append({
            'final_score': round(example_score, 2),
            'word_accuracy': round(example_word_accuracy * 100, 2),
            'word_order_distance': round(example_order_distance, 2),
            'is_correct': is_exact_match
        })

    # Calculate overall metrics from stored individual results
    efficiency_modifier = calculate_efficiency_modifier(len(prompt), "word_sorting")
    accuracy = sum(all_exact_matches) / len(all_exact_matches) if all_exact_matches else 0
    word_accuracy = sum(all_word_accuracies) / len(all_word_accuracies) if all_word_accuracies else 0
    avg_order_distance = sum(all_order_distances) / len(all_order_distances) if all_order_distances else 1
    
    combined_score = (
        (accuracy * 0.4) +
        (word_accuracy * 0.4) +
        ((1 - avg_order_distance) * 0.2)
    ) * efficiency_modifier * 100

    return {
        'accuracy': round(accuracy * 100, 2),
        'word_accuracy': round(word_accuracy * 100, 2),
        'word_order_distance': round(avg_order_distance, 2),
        'combined_score': round(combined_score, 2),
        'prompt_length': len(prompt),
        'efficiency_modifier': efficiency_modifier,
        'total_tests': len(expected_outputs),
        'correct_count': sum(all_exact_matches),
        'individual_scores': individual_scores
    }