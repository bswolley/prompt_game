from typing import List
import re
from difflib import get_close_matches

def extract_relevant_words(response: str, expected_words: str) -> str:
    """
    Extract and match words from response that appear in expected words.
    Handles fuzzy matching and deduplication.
    
    Args:
        response: The model's response text
        expected_words: String containing the expected words
        
    Returns:
        String of relevant words found in response, space-separated
    """
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
    
    # Remove duplicates while preserving order
    seen = set()
    unique_words = [word for word in relevant_words if not (word in seen or seen.add(word))]
    return ' '.join(unique_words)

def calculate_kendall_tau_distance(list1: List[str], list2: List[str]) -> float:
    """
    Calculate normalized Kendall tau distance between two lists.
    Measures the number of swaps needed to transform one ordering into another.
    
    Args:
        list1: First list of items
        list2: Second list of items
        
    Returns:
        Float between 0 and 1, where 0 means identical ordering and 1 means completely reversed
    """
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
    Longer prompts get lower modifiers to encourage conciseness.
    
    Args:
        prompt_length: Length of the system prompt in characters
        dataset_type: Type of dataset ("word_sorting", "logical_deduction", or "causal_judgement")
        
    Returns:
        Float between 0 and 1 representing the efficiency modifier
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
        elif prompt_length <= 20:
            return 0.9
        elif prompt_length <= 30:
            return 0.8
        elif prompt_length <= 40:
            return 0.7
        elif prompt_length <= 50:
            return 0.6
        else:
            return 0.5
        
        # Add to calculate_efficiency_modifier function in utils.py
    elif dataset_type == "summarization":
        if prompt_length <= 20:
            return 1.0
        elif prompt_length <= 40:
            return 0.9
        elif prompt_length <= 60:
            return 0.8
        elif prompt_length <= 80:
            return 0.7
        elif prompt_length <= 100:
            return 0.6
        else:
            return 0.5
            
    return 1.0  # Default case

def format_percentage(value: float, decimal_places: int = 2) -> float:
    """
    Helper function to format percentage values.
    
    Args:
        value: Raw decimal value (e.g., 0.756)
        decimal_places: Number of decimal places to round to
        
    Returns:
        Formatted percentage (e.g., 75.60)
    """
    return round(value * 100, decimal_places)

def cap_score(score: float, max_value: float = 100.0) -> float:
    """
    Helper function to cap a score at a maximum value.
    
    Args:
        score: Raw score value
        max_value: Maximum allowed value
        
    Returns:
        Score capped at max_value
    """
    return min(score, max_value)