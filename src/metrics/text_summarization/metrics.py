from typing import List, Dict
import spacy
import numpy as np
from src.metrics.utils import calculate_efficiency_modifier

# Initialize spaCy with the medium model
nlp = spacy.load("en_core_web_md")

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts."""
    doc1 = nlp(text1.lower())
    doc2 = nlp(text2.lower())
    return doc1.similarity(doc2)
def calculate_length_penalty(expected_length: int, actual_length: int) -> float:
    """
    Calculate length penalty based on ratio between actual and expected length.
    - No penalty for within 20% of expected length
    - Then decreases in 10% bands
    - Equal penalties for being too short or too long
    
    Args:
        expected_length (int): Target length in characters
        actual_length (int): Actual length in characters
    
    Returns:
        float: Penalty factor between 0 and 1
    """
    # Calculate ratio of actual to expected length
    ratio = actual_length / expected_length
    
    # Debug print
    print(f"Length penalty calculation:")
    print(f"Expected length: {expected_length}, Actual length: {actual_length}")
    print(f"Ratio: {ratio:.2f}")

    # Within 20% of expected length - no penalty
    if 0.8 <= ratio <= 1.2:
        print("Within 20% - No penalty")
        return 1.0
    
    # 20-30% off (either direction)
    elif 0.7 <= ratio < 0.8 or 1.2 < ratio <= 1.3:
        print("20-30% off - Penalty: 0.9")
        return 0.9
    
    # 30-40% off (either direction)
    elif 0.6 <= ratio < 0.7 or 1.3 < ratio <= 1.4:
        print("30-40% off - Penalty: 0.8")
        return 0.8
    
    # 40-50% off (either direction)
    elif 0.5 <= ratio < 0.6 or 1.4 < ratio <= 1.5:
        print("40-50% off - Penalty: 0.7")
        return 0.7
    
    # More than 50% off (either direction)
    else:
        print("More than 50% off - Penalty: 0.6")
        return 0.6

def calculate_summarization_metrics(
    expected_outputs: List[str],
    model_predictions: List[str],
    system_prompt: str
) -> Dict:
    """Calculate metrics for text summarization tasks."""
    print("\nCalculating summarization metrics...")
    total_examples = len(expected_outputs)
    similarities = []
    individual_scores = []
    length_penalties = []
    actual_lengths = []

    # Process each example
    for i, (true_summary, model_summary) in enumerate(zip(expected_outputs, model_predictions)):
        try:
            print(f"\nProcessing example {i + 1}:")
            # Calculate similarity
            similarity = calculate_similarity(true_summary, model_summary)
            print(f"Similarity: {similarity}")

            # Calculate lengths
            expected_length = len(true_summary)
            actual_length = len(model_summary)
            print(f"Expected length: {expected_length}, Actual length: {actual_length}")

            # Calculate length penalty
            length_penalty = calculate_length_penalty(expected_length, actual_length)
            print(f"Length penalty: {length_penalty}")
            
            similarities.append(similarity)
            length_penalties.append(length_penalty)
            actual_lengths.append(actual_length)

            # Store individual scores
            individual_scores.append({
                'similarity': round(similarity * 100, 2),
                'length_penalty': round(length_penalty * 100, 2),
                'actual_length': actual_length,
                'expected_length': expected_length
            })
            
        except Exception as e:
            print(f"Error processing example {i + 1}: {str(e)}")
            similarities.append(0)
            length_penalties.append(0)
            actual_lengths.append(0)
            individual_scores.append({
                'similarity': 0,
                'length_penalty': 0,
                'actual_length': 0,
                'expected_length': expected_length
            })

    # Calculate averages
    avg_similarity = np.mean(similarities) if similarities else 0
    avg_length_penalty = np.mean(length_penalties) if length_penalties else 0
    avg_actual_length = np.mean(actual_lengths) if actual_lengths else 0

    # Calculate prompt efficiency
    prompt_efficiency = calculate_efficiency_modifier(len(system_prompt), "summarization")
    print(f"\nPrompt efficiency: {prompt_efficiency}")

    # Calculate final score (similarity × length penalty × prompt efficiency)
    final_score = avg_similarity * avg_length_penalty * prompt_efficiency
    print(f"Final score components: {avg_similarity} × {avg_length_penalty} × {prompt_efficiency}")

    # Prepare results
    results = {
        'final_score': round(final_score * 100, 2),
        'similarity': round(avg_similarity * 100, 2),
        'prompt_efficiency': round(prompt_efficiency * 100, 2),
        'length_penalty_avg': round(avg_length_penalty * 100, 2),
        'prompt_length_chars': len(system_prompt),
        'average_actual_length_chars': round(avg_actual_length, 1),
        'total_tests': total_examples,
        'individual_scores': individual_scores
    }
    
    print("\nFinal metrics:", results)
    return results