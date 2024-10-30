import re
from difflib import get_close_matches

def extract_relevant_words(response, expected_words):
    """Extract words from the model response that are close matches to the expected list."""
    expected_words_list = expected_words.lower().split()
    all_words = re.findall(r"\b[\w\.\-&']+\b", response.lower())
    relevant_words = []
    
    for word in all_words:
        if word in expected_words_list:
            relevant_words.append(word)
        else:
            close_match = get_close_matches(word, expected_words_list, n=1, cutoff=0.9)
            if close_match:
                relevant_words.append(close_match[0])
    
    seen = set()
    unique_words = [word for word in relevant_words if not (word in seen or seen.add(word))]
    return ' '.join(unique_words)

def calculate_kendall_tau_distance(list1, list2):
    if len(list1) != len(list2) or set(list1) != set(list2):
        return 1.0
    pos1 = {word: i for i, word in enumerate(list1)}
    swaps = 0
    n = len(list1)
    for i in range(n):
        for j in range(i + 1, n):
            if pos1[list2[i]] > pos1[list2[j]]:
                swaps += 1
    max_swaps = (n * (n - 1)) // 2
    return swaps / max_swaps if max_swaps > 0 else 0

def calculate_metrics(expected_outputs, model_predictions):
    processed_predictions = []
    processed_outputs = []
    
    for exp, pred in zip(expected_outputs, model_predictions):
        processed_pred = extract_relevant_words(pred, exp)
        processed_predictions.append(processed_pred)
        processed_outputs.append(exp.strip())
    
    correct = sum(1 for exp, pred in zip(processed_outputs, processed_predictions) if exp == pred)
    accuracy = correct / len(processed_outputs)
    
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
    avg_word_order_distance = sum(word_order_distances) / len(word_order_distances)
    
    metrics = {
        'accuracy': round(accuracy * 100, 2),
        'word_order_distance': round(avg_word_order_distance, 2),
        'word_accuracy': round(word_accuracy * 100, 2),
        'total_tests': len(processed_outputs),
        'correct_count': correct,
        'combined_score': calculate_combined_score({
            'accuracy': accuracy, 
            'word_accuracy': word_accuracy, 
            'word_order_distance': avg_word_order_distance
        })
    }
    
    return metrics

def calculate_combined_score(metrics):
    accuracy_weight = 0.4
    word_accuracy_weight = 0.4
    distance_weight = 0.2
    distance_score = (1 - metrics['word_order_distance']) * 100
    combined_score = (
        (metrics['accuracy'] * 100 * accuracy_weight) +
        (metrics['word_accuracy'] * 100 * word_accuracy_weight) +
        (distance_score * distance_weight)
    )
    return round(combined_score, 2)