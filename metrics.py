import re
from difflib import get_close_matches

def standardize_logical_answer(answer: str) -> str:
    """
    Standardize logical deduction answers to format (X) where X is a single letter A-G.
    Handles various formats:
    - "A" -> "(A)"
    - "a" -> "(A)"
    - "(A)" -> "(A)"
    - " A " -> "(A)"
    - "The answer is A" -> "(A)"
    - "The correct answer is (A)" -> "(A)"
    - "Answer: A" -> "(A)"
    - "Therefore, B is correct" -> "(B)"
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
    
    # Look for any single letter A-G, prioritizing those that appear alone or with common markers
    letter_matches = re.findall(r'(?:^|\s)([A-G])(?:\s|$|\.|\,|\:|\)|\()', clean_answer)
    if letter_matches:
        # If there are multiple matches, take the first one
        return f"({letter_matches[0]})"
    
    # Last resort: just look for any A-G in the string
    any_letter = re.search(r'[A-G]', clean_answer)
    if any_letter:
        return f"({any_letter.group(0)})"
    
    # If no valid letter found, return original cleaned answer
    return clean_answer

def is_properly_formatted(answer: str) -> bool:
    """
    Check if the raw answer is already in proper format: either 'A' or '(A)' for any letter A-G
    """
    # Clean the answer of whitespace
    clean = answer.strip().upper()
    # Check for single letter format
    if clean in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return True
    # Check for parentheses format
    if clean in ['(A)', '(B)', '(C)', '(D)', '(E)', '(F)', '(G)']:
        return True
    return False

def extract_relevant_words(response, expected_words):
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

def calculate_efficiency_modifier(prompt_length: int, dataset_type: str = "word_sorting") -> float:
    """
    Calculate efficiency modifier based on prompt length and dataset type.
    """
    if dataset_type == "word_sorting":
        if prompt_length <= 8:
            return 1.0
        elif prompt_length <= 12:
            return 0.95
        elif prompt_length <= 20:
            return 0.9
        elif prompt_length <= 40:
            return 0.8
        elif prompt_length <= 60:
            return 0.7
        else:
            return 0.6
    elif dataset_type == "logical_deduction":
        if prompt_length <= 10:
            return 1.0
        elif prompt_length <= 20:
            return 0.95
        elif prompt_length <= 30:
            return 0.9
        elif prompt_length <= 50:
            return 0.8
        elif prompt_length <= 70:
            return 0.7
        elif prompt_length <= 100:
            return 0.6
        elif prompt_length <= 200:
            return 0.5
        else:
            return 0.4
    elif dataset_type == "causal_judgement":
        if prompt_length <= 10:
            return 1.0
        elif prompt_length <= 20 :
            return 0.9
        elif prompt_length <= 30:
            return 0.8
        elif prompt_length <= 40:
            return 0.7
        elif prompt_length <= 50:
            return 0.6
        else:
            return 0.5
    return 1.0  # Default case

def calculate_metrics(expected_outputs, model_predictions, prompt: str):
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

    processed_predictions = []
    processed_outputs = []
    
    for exp, pred in zip(expected_outputs, model_predictions):
        processed_pred = extract_relevant_words(pred, exp)
        processed_predictions.append(processed_pred)
        processed_outputs.append(exp.strip())
    
    correct = sum(1 for exp, pred in zip(processed_outputs, processed_predictions) if exp == pred)
    accuracy = correct / len(processed_outputs) if processed_outputs else 0
    
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

    prompt_length = len(prompt)
    efficiency_modifier = calculate_efficiency_modifier(prompt_length, "word_sorting")
    
    # Calculate component scores
    accuracy_contribution = accuracy * 0.4
    word_accuracy_contribution = word_accuracy * 0.4
    distance_contribution = (1 - avg_word_order_distance) * 0.2
    
    base_combined_score = accuracy_contribution + word_accuracy_contribution + distance_contribution
    combined_score = base_combined_score * efficiency_modifier
    
    # Scale the combined score to a percentage
    combined_score_percentage = combined_score * 100

    return {
        'accuracy': round(accuracy * 100, 2),
        'word_accuracy': round(word_accuracy * 100, 2),
        'word_order_distance': round(avg_word_order_distance, 2),
        'combined_score': round(combined_score_percentage, 2),
        'prompt_length': prompt_length,
        'efficiency_modifier': efficiency_modifier,
        'total_tests': len(processed_outputs),
        'correct_count': correct
    }

def calculate_logical_deduction_metrics(expected_outputs, model_predictions, system_prompt):
    # Standardize outputs and predictions
    standardized_expected = [standardize_logical_answer(exp) for exp in expected_outputs]
    standardized_predictions = [standardize_logical_answer(pred) for pred in model_predictions]
    
    # Calculate base accuracy
    correct_count = sum(1 for exp, pred in zip(standardized_expected, standardized_predictions) 
                       if exp == pred)
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests) * 100 if total_tests > 0 else 0
    
    # Calculate format bonus points
    format_bonus = sum(1 for pred, std_pred, exp in zip(model_predictions, standardized_predictions, standardized_expected) 
                      if is_properly_formatted(pred) and std_pred == exp)
    
    # Calculate efficiency modifier
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "logical_deduction")
    
    # Calculate final accuracy with bonus
    # First apply efficiency modifier to base accuracy
    efficiency_adjusted_accuracy = base_accuracy * efficiency_modifier
    
    # Add 1 percentage point for each correctly formatted answer
    bonus_points = (format_bonus / total_tests) * 1  # 1 point per correct formatted answer
    final_accuracy = efficiency_adjusted_accuracy
    
    # Cap the final accuracy at 100%
    final_accuracy = min(100, final_accuracy)
    
    return {
        'accuracy': round(final_accuracy, 2),
        'base_accuracy': round(base_accuracy, 2),
        'format_bonus': format_bonus,
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': standardized_predictions
    }

def calculate_causal_judgment_metrics(expected_outputs, model_predictions, system_prompt):
    """
    Calculate metrics for causal judgment predictions.
    Similar to logical deduction but without letter standardization.
    
    Args:
        expected_outputs: List of expected answers
        model_predictions: List of model's predicted answers
        system_prompt: The system prompt used
        
    Returns:
        Dictionary containing accuracy metrics
    """
    # Calculate base accuracy
    correct_count = sum(1 for exp, pred in zip(expected_outputs, model_predictions) 
                       if exp.strip().lower() == pred.strip().lower())
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests) * 100 if total_tests > 0 else 0
    
    # Calculate efficiency modifier using the same logic as logical deduction
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "logical_deduction")
    
    # Apply efficiency modifier to base accuracy
    final_accuracy = base_accuracy * efficiency_modifier
    
    # Cap the final accuracy at 100%
    final_accuracy = min(100, final_accuracy)
    
    return {
        'accuracy': round(final_accuracy, 2),
        'base_accuracy': round(base_accuracy, 2),
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': [pred.strip().lower() for pred in model_predictions]  # Keep for consistency with other metrics
    }

# Optional testing function - can be commented out in production
def test_logical_parser():
    test_cases = [
        ("A", "(A)"),
        ("(B)", "(B)"),
        (" C ", "(C)"),
        ("The answer is D", "(D)"),
        ("The correct answer is (E)", "(E)"),
        ("Answer: F", "(F)"),
        ("Therefore, G must be correct", "(G)"),
        ("Based on the given information, A is the correct answer.", "(A)"),
        ("After analyzing the sequence, the answer has to be (B).", "(B)"),
        ("Looking at the pattern, we can conclude that C.", "(C)"),
        ("Through logical deduction, D would be correct.", "(D)"),
        ("This means E is the answer.", "(E)"),
        ("Given these conditions, F should be chosen.", "(F)"),
        ("The solution points to G.", "(G)"),
    ]
    
    for test_input, expected in test_cases:
        result = standardize_logical_answer(test_input)
        print(f"Input: {test_input}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        print(f"Pass: {result == expected}\n")

def standardize_causal_answer(answer: str) -> str:
    """
    Standardize causal judgment answers to 'yes' or 'no'.
    Handles various formats:
    - "Yes" -> "yes"
    - "No" -> "no"
    - "The answer is yes" -> "yes"
    - "Therefore, no" -> "no"
    - "I think yes" -> "yes"
    - "Based on this, no" -> "no"
    """
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
    
    # Remove common phrases
    for phrase in phrases_to_remove:
        clean_answer = clean_answer.replace(phrase, "")
    
    # Clean up extra whitespace
    clean_answer = " ".join(clean_answer.split())
    
    # Look for yes/no in the cleaned answer
    if 'yes' in clean_answer.split() or clean_answer.endswith('yes'):
        return 'yes'
    if 'no' in clean_answer.split() or clean_answer.endswith('no'):
        return 'no'
    
    # Check for other affirmative/negative expressions
    affirmative = ['correct', 'true', 'right', 'indeed', 'affirmative', 'absolutely']
    negative = ['incorrect', 'false', 'wrong', 'negative', 'nope', 'nah']
    
    for word in clean_answer.split():
        if word in affirmative:
            return 'yes'
        if word in negative:
            return 'no'
    
    # If no clear yes/no found, return original cleaned answer
    return clean_answer

def is_valid_causal_answer(answer: str) -> bool:
    """
    Check if the raw answer is a clear yes/no response
    """
    clean = answer.strip().lower()
    # Direct yes/no
    if clean in ['yes', 'no']:
        return True
    # Simple variations
    if clean in ['yes.', 'no.', 'yes!', 'no!']:
        return True
    return False

def standardize_causal_answer(answer: str) -> str:
    """
    Standardize causal judgment answers to 'Yes' or 'No'.
    Handles various formats:
    - "Yes." -> "Yes"
    - "No!" -> "No"
    - "The answer is yes" -> "Yes"
    - "Therefore, no" -> "No"
    """
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
    
    # Remove common phrases
    for phrase in phrases_to_remove:
        clean_answer = clean_answer.replace(phrase, "")
        
    # Remove punctuation
    clean_answer = clean_answer.replace('.', '').replace('!', '').replace(',', '').replace(':', '')
    
    # Clean up extra whitespace
    clean_answer = " ".join(clean_answer.split())
    
    # Look for yes/no in the cleaned answer
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
    
    # If no clear yes/no found, return original cleaned answer
    return clean_answer

# Also update calculate_causal_judgment_metrics
def calculate_causal_judgment_metrics(expected_outputs, model_predictions, system_prompt):
    """
    Calculate metrics for causal judgment predictions.
    """
    # Standardize outputs and predictions
    standardized_expected = [exp.strip() for exp in expected_outputs]  # Keep original Yes/No case
    standardized_predictions = [standardize_causal_answer(pred) for pred in model_predictions]
    
    # Calculate base accuracy
    correct_count = sum(1 for exp, pred in zip(standardized_expected, standardized_predictions) 
                       if exp == pred)
    total_tests = len(expected_outputs)
    base_accuracy = (correct_count / total_tests) * 100 if total_tests > 0 else 0
    
    # Calculate format bonus points for clear yes/no answers
    format_bonus = sum(1 for pred in standardized_predictions if pred in ['Yes', 'No'])
    
    # Calculate efficiency modifier
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "logical_deduction")
    
    # Apply efficiency modifier to base accuracy
    final_accuracy = base_accuracy * efficiency_modifier
    
    # Cap the final accuracy at 100%
    final_accuracy = min(100, final_accuracy)
    
    return {
        'accuracy': round(final_accuracy, 2),
        'base_accuracy': round(base_accuracy, 2),
        'format_bonus': format_bonus,
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_tests,
        'correct_count': correct_count,
        'standardized_outputs': standardized_predictions
    }

# Uncomment to run tests
# if __name__ == "__main__":
#     test_logical_parser()