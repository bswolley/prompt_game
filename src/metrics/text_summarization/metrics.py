from typing import List, Dict
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from bert_score import score
from ..utils import calculate_efficiency_modifier, format_percentage

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

def get_embedding(text: str) -> np.ndarray:
    """Get document embedding using spaCy"""
    doc = nlp(text)
    return doc.vector

def calculate_similarity(true_summary: str, model_summary: str) -> float:
    """Calculate semantic similarity between two texts using spaCy embeddings"""
    true_embedding = get_embedding(true_summary).reshape(1, -1)
    model_embedding = get_embedding(model_summary).reshape(1, -1)
    
    if np.all(true_embedding == 0) or np.all(model_embedding == 0):
        return 0.0
        
    similarity = cosine_similarity(true_embedding, model_embedding)[0][0]
    return float(similarity)

def calculate_bertscore(true_summary: str, model_summary: str) -> float:
    """Calculate BERTScore for the summaries"""
    P, R, F1 = score([model_summary], [true_summary], lang='en', verbose=False)
    return F1.item()

def calculate_combined_score(semantic_sim: float, bertscore: float) -> float:
    """Calculate combined score (50% semantic similarity, 50% BERTScore)"""
    return 0.5 * semantic_sim + 0.5 * bertscore

def calculate_metrics(expected_outputs: List[str], model_predictions: List[str], system_prompt: str) -> Dict:
    """
    Calculate metrics for text summarization task.
    
    Args:
        expected_outputs: List of expected summaries
        model_predictions: List of model's generated summaries
        system_prompt: The prompt used for generation
    
    Returns:
        Dictionary containing various metrics
    """
    total_examples = len(expected_outputs)
    semantic_similarities = []
    bertscores = []
    combined_scores = []
    
    for true_summary, model_summary in zip(expected_outputs, model_predictions):
        try:
            # Calculate semantic similarity
            semantic_sim = calculate_similarity(true_summary, model_summary)
            semantic_similarities.append(semantic_sim)
            
            # Calculate BERTScore
            bertscore = calculate_bertscore(true_summary, model_summary)
            bertscores.append(bertscore)
            
            # Calculate combined score
            combined = calculate_combined_score(semantic_sim, bertscore)
            combined_scores.append(combined)
            
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            semantic_similarities.append(0)
            bertscores.append(0)
            combined_scores.append(0)
    
    # Calculate averages
    avg_semantic = sum(semantic_similarities) / total_examples if total_examples > 0 else 0
    avg_bertscore = sum(bertscores) / total_examples if total_examples > 0 else 0
    avg_combined = sum(combined_scores) / total_examples if total_examples > 0 else 0
    
    # Calculate efficiency modifier
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "summarization")
    
    # Apply efficiency modifier to final score
    final_score = avg_combined * efficiency_modifier
    
    # Count summaries above quality threshold
    quality_threshold = 0.6
    good_summaries = sum(1 for score in combined_scores if score >= quality_threshold)
    
    return {
        'accuracy': format_percentage(final_score),
        'semantic_similarity': format_percentage(avg_semantic),
        'bertscore': format_percentage(avg_bertscore),
        'combined_score': format_percentage(avg_combined),
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': total_examples,
        'good_summaries': good_summaries,
        'quality_rate': format_percentage(good_summaries / total_examples if total_examples > 0 else 0),
        'per_example_scores': [
            {
                'semantic_similarity': format_percentage(sem),
                'bertscore': format_percentage(bert),
                'combined_score': format_percentage(comb)
            }
            for sem, bert, comb in zip(semantic_similarities, bertscores, combined_scores)
        ],
        'standardized_outputs': model_predictions  # Keep consistent with other metrics
    }