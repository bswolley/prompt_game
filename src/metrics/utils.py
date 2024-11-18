from typing import List
import re
from difflib import get_close_matches

def extract_relevant_words(response: str, expected_words: str) -> str:
    """
    Extract words from the response that match or closely match expected words,
    with deduplication.
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
    Calculate normalized Kendall tau distance between two lists of words.
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
    Calculate an efficiency modifier based on prompt length and dataset type.
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
        if prompt_length <= 8:
            return 1.0
        elif prompt_length <= 10:
            return 0.975
        elif prompt_length <= 12:
            return 0.95
        elif prompt_length <= 16:
            return 0.9
        elif prompt_length <= 32:
            return 0.7
        elif prompt_length <= 48:
            return 0.6
        else:
            return 0.5
        
    elif dataset_type == "summarization":
        if prompt_length <= 20:
            return 1.0
        elif prompt_length <= 25:
            return 0.975
        elif prompt_length <= 30:
            return 0.95
        elif prompt_length <= 40:
            return 0.9
        elif prompt_length <= 50:
            return 0.8
        elif prompt_length <= 60:
            return 0.7
        elif prompt_length <= 70:
            return 0.6
        else:
            return 0.5
            
    return 1.0  # Default case

def format_percentage(value: float, decimal_places: int = 2) -> float:
    """
    Format a float as a percentage rounded to the specified decimal places.
    """
    return round(value * 100, decimal_places)

def cap_score(score: float, max_value: float = 100.0) -> float:
    """
    Cap a score at a specified maximum value.
    """
    return min(score, max_value)
