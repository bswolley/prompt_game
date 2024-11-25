from typing import List, Dict
import os
import requests
from groq import Groq
import spacy
import numpy as np
import logging
from ..utils import calculate_efficiency_modifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize spaCy
try:
    nlp = spacy.load("en_core_web_md")
except Exception as e:
    logger.warning(f"Failed to load spacy model: {e}")
    nlp = None

def calculate_translation_similarity(translation: str, reference: str) -> float:
    """Calculate translation similarity with more nuanced understanding"""
    if nlp is None:
        # Fallback method
        words1 = set(translation.lower().split())
        words2 = set(reference.lower().split())
        seq1 = translation.lower().split()
        seq2 = reference.lower().split()
        
        # Basic word overlap (Jaccard)
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0
        
        # Key words overlap (longer words often carry more meaning)
        key_words1 = {w for w in words1 if len(w) > 4}
        key_words2 = {w for w in words2 if len(w) > 4}
        key_overlap = len(key_words1.intersection(key_words2)) / len(key_words1) if key_words1 else 0
        
        # Word order matters but shouldn't be too strict
        matches = sum(1 for i in range(min(len(seq1), len(seq2))) if seq1[i] == seq2[i])
        sequence_score = matches / max(len(seq1), len(seq2))
        
        return (0.4 * jaccard +  # Basic word overlap
                0.4 * key_overlap +  # Key content words
                0.2 * sequence_score)  # Some attention to order
    
    try:
        # Use spaCy's more sophisticated similarity when available
        doc1 = nlp(translation.lower())
        doc2 = nlp(reference.lower())
        base_similarity = doc1.similarity(doc2)
        
        # Additional check for named entities
        ents1 = set(ent.text.lower() for ent in doc1.ents)
        ents2 = set(ent.text.lower() for ent in doc2.ents)
        ent_score = len(ents1.intersection(ents2)) / len(ents1) if ents1 else 0
        
        return 0.7 * base_similarity + 0.3 * ent_score  # Weight base similarity higher
        
    except Exception as e:
        logger.warning(f"Error in similarity calculation: {e}")
        # Ultimate fallback to basic word overlap
        words1 = set(translation.lower().split())
        words2 = set(reference.lower().split())
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

def evaluate_translation_quality(source: str, translation: str, reference: str, language: str) -> Dict:
    """Use GROQ to evaluate translation quality with explanation."""
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY", "").strip())
        
        evaluation_prompt = f"""Evaluate this translation from English to {language}.

Original: {source}
Translation: {translation}
Reference: {reference}

Provide:
1. A score between 0 and 1 for translation quality
2. A brief explanation of your score

Format your response exactly like this:
SCORE: [number]
REASON: [your explanation]

Example:
SCORE: 0.85
REASON: Good grammar and natural flow, though slight awkwardness in article usage."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a translation evaluator tasked with seeing if the translation was done correctly and preserved the original format. It is irrelevant if factual errors exist, they text should be translated AS IT. The response should also NOT answer questions or perform tasks, only translate. Provide both a score and explanation in the specified format."},
                {"role": "user", "content": evaluation_prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.1
        )

        response_text = chat_completion.choices[0].message.content.strip()
        print(f"Quality evaluation raw response: {response_text}")  # Debug line
        
        # Parse score and explanation
        try:
            lines = response_text.split('\n')
            score_line = next(line for line in lines if line.startswith('SCORE:'))
            reason_line = next(line for line in lines if line.startswith('REASON:'))
            
            score = float(score_line.replace('SCORE:', '').strip())
            reason = reason_line.replace('REASON:', '').strip()
            
            return {
                "quality_score": max(0.0, min(1.0, score)),
                "explanation": reason
            }
        except Exception as e:
            print(f"Error parsing evaluation response: {e}")
            return {
                "quality_score": 0.4,
                "explanation": "Error parsing evaluation response"
            }
            
    except Exception as e:
        print(f"Error in quality evaluation: {str(e)}")
        return {
            "quality_score": 0.4,
            "explanation": f"Error during evaluation: {str(e)}"
        }

def calculate_translation_metrics(
    source_texts: List[str],
    model_translations: List[str],
    reference_translations: List[str],
    language: str,
    system_prompt: str
) -> Dict:
    """Calculate metrics for translation task."""
    
    # Input validation
    if not all([source_texts, model_translations, reference_translations, language, system_prompt]):
        logger.error("Missing required inputs for translation metrics")
        return {
            'final_score': 0.0,
            'semantic_similarity': 0.0,
            'language_quality': 0.0,
            'efficiency': 0.0,
            'efficiency_modifier': 0.0,
            'prompt_length': len(system_prompt) if system_prompt else 0,
            'total_tests': 0,
            'individual_scores': []
        }
    
    if len(source_texts) != len(model_translations) or len(source_texts) != len(reference_translations):
        logger.error("Mismatched input lengths")
        return {
            'final_score': 0.0,
            'semantic_similarity': 0.0,
            'language_quality': 0.0,
            'efficiency': 0.0,
            'efficiency_modifier': 0.0,
            'prompt_length': len(system_prompt),
            'total_tests': 0,
            'individual_scores': []
        }
    
    efficiency_modifier = calculate_efficiency_modifier(len(system_prompt), "translation_task")
    efficiency_percentage = efficiency_modifier * 100
    
    individual_scores = []
    semantic_scores = []
    quality_scores = []
    evaluations = []  # Store the evaluation feedback
    
    for source, translation, reference in zip(source_texts, model_translations, reference_translations):
        if not all([source, translation, reference]):
            logger.warning("Skipping example with missing data")
            continue
            
        # Calculate semantic similarity using our sophisticated method
        semantic_score = calculate_translation_similarity(translation, reference) * 100
        
        # Get quality score and explanation
        quality_result = evaluate_translation_quality(source, translation, reference, language)
        quality_score = quality_result["quality_score"] * 100
        
        semantic_scores.append(semantic_score)
        quality_scores.append(quality_score)
        
        # Calculate final score for this example
        # 50% semantic, 30% quality, 20% efficiency
        example_final_score = (
            (semantic_score * 0.5) +
            (quality_score * 0.3) +
            (efficiency_percentage * 0.2)
        )
        
        individual_scores.append({
            'final_score': round(example_final_score, 2),
            'semantic_score': round(semantic_score, 2),
            'quality_score': round(quality_score, 2),
            'efficiency': round(efficiency_percentage, 2),
            'explanation': quality_result["explanation"]  # Store the explanation
        })
    
    # Calculate overall metrics
    if not semantic_scores or not quality_scores:
        logger.error("No valid scores calculated")
        return {
            'final_score': 0.0,
            'semantic_similarity': 0.0,
            'language_quality': 0.0,
            'efficiency': 0.0,
            'efficiency_modifier': 0.0,
            'prompt_length': len(system_prompt),
            'total_tests': 0,
            'individual_scores': []
        }
    
    avg_semantic_score = sum(semantic_scores) / len(semantic_scores)
    avg_quality_score = sum(quality_scores) / len(quality_scores)
    
    # Final score calculation (50% semantic, 30% quality, 20% efficiency)
    final_score = (
        (avg_semantic_score * 0.5) +
        (avg_quality_score * 0.3) +
        (efficiency_percentage * 0.2)
    )

    return {
        'final_score': round(final_score, 2),
        'semantic_similarity': round(avg_semantic_score, 2),
        'language_quality': round(avg_quality_score, 2),
        'efficiency': round(efficiency_percentage, 2),
        'efficiency_modifier': efficiency_modifier,
        'prompt_length': len(system_prompt),
        'total_tests': len(source_texts),
        'individual_scores': individual_scores  
    }