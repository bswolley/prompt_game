from typing import List, Dict
import spacy
import numpy as np
from src.metrics.utils import calculate_efficiency_modifier
import time
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_md")
except Exception as e:
    logger.warning(f"Failed to load spacy model: {e}")
    nlp = None

def calculate_similarity(text1: str, text2: str) -> float:
    if nlp is None:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        seq1 = text1.lower().split()
        seq2 = text2.lower().split()
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0
        
        key_words1 = {w for w in words1 if len(w) > 4}
        key_words2 = {w for w in words2 if len(w) > 4}
        key_overlap = len(key_words1.intersection(key_words2)) / len(key_words1) if key_words1 else 0
        
        matches = sum(1 for i in range(min(len(seq1), len(seq2))) if seq1[i] == seq2[i])
        sequence_score = matches / max(len(seq1), len(seq2))
        
        return 0.3 * jaccard + 0.5 * key_overlap + 0.2 * sequence_score
    
    try:
        doc1 = nlp(text1.lower())
        doc2 = nlp(text2.lower())
        base_similarity = doc1.similarity(doc2)
        
        ents1 = set(ent.text.lower() for ent in doc1.ents)
        ents2 = set(ent.text.lower() for ent in doc2.ents)
        ent_score = len(ents1.intersection(ents2)) / len(ents1) if ents1 else 0
        
        return 0.6 * base_similarity + 0.4 * ent_score
        
    except Exception as e:
        logger.warning(f"Error in similarity calculation: {e}")
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

def calculate_length_penalty(expected_length: int, actual_length: int) -> float:
    ratio = actual_length / expected_length
    
    if 0.75 <= ratio <= 1.25:
        return 1.0
    elif 0.6 <= ratio < 0.75 or 1.25 < ratio <= 1.4:
        return 0.9
    elif 0.5 <= ratio < 0.75 or 1.4 < ratio <= 1.6:
        return 0.8
    elif 0.3 <= ratio < 0.5 or 1.6 < ratio <= 1.8:
        return 0.7
    elif 0.01 <= ratio < 0.3 or 1.8 < ratio <= 1.99:
        return 0.6
    else:
        return 0.5

def assess_quality(metrics: Dict) -> Dict:
    similarity = metrics['similarity']
    length_penalty = metrics['length_penalty']
    
    if similarity >= 80:
        quality = "Well done ✓"
    elif similarity >= 60:
        quality = "Could be improved ⚠️"
    else:
        quality = "Needs improvement ✗"
    
    feedback = []
    if similarity < 75:
        feedback.append("Content preservation needs improvement")
    if length_penalty < 80:
        feedback.append("Length consistency needs attention")
        
    return {
        'rating': quality,
        'feedback': feedback
    }

def calculate_summarization_metrics(
    expected_outputs: List[str],
    model_predictions: List[str],
    system_prompt: str
) -> Dict:
    total_examples = len(expected_outputs)
    similarities = []
    individual_scores = []
    length_penalties = []
    actual_lengths = []

    for i, (true_summary, model_summary) in enumerate(zip(expected_outputs, model_predictions)):
        try:
            similarity = calculate_similarity(true_summary, model_summary)
            expected_length = len(true_summary)
            actual_length = len(model_summary)
            length_penalty = calculate_length_penalty(expected_length, actual_length)
            
            similarities.append(similarity)
            length_penalties.append(length_penalty)
            actual_lengths.append(actual_length)

            individual_scores.append({
                'similarity': round(similarity * 100, 2),
                'length_penalty': round(length_penalty * 100, 2),
                'actual_length': actual_length,
                'expected_length': expected_length
            })
            
        except Exception as e:
            logger.error(f"Error processing example {i + 1}: {str(e)}")
            similarities.append(0)
            length_penalties.append(0)
            actual_lengths.append(0)
            individual_scores.append({
                'similarity': 0,
                'length_penalty': 0,
                'actual_length': 0,
                'expected_length': expected_length
            })

    avg_similarity = np.mean(similarities) if similarities else 0
    avg_length_penalty = np.mean(length_penalties) if length_penalties else 0
    avg_actual_length = np.mean(actual_lengths) if actual_lengths else 0
    prompt_efficiency = calculate_efficiency_modifier(len(system_prompt), "summarization")
    final_score = avg_similarity * ((avg_length_penalty + prompt_efficiency) / 2)

    results = {
        'final_score': round(final_score * 100, 2),
        'similarity': round(avg_similarity * 100, 2),
        'prompt_efficiency': round(prompt_efficiency * 100, 2),
        'length_penalty_avg': round(avg_length_penalty * 100, 2),
        'prompt_length_chars': len(system_prompt),
        'average_actual_length_chars': round(avg_actual_length, 1),
        'total_tests': total_examples,
        'individual_scores': individual_scores,
        'quality_assessment': assess_quality({
            'similarity': avg_similarity * 100,
            'length_penalty': avg_length_penalty * 100
        })
    }
    
    return results