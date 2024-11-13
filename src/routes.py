from flask import Blueprint, request, jsonify, render_template
from groq import Groq
import os
from src.config import get_config
from src.metrics import (
    calculate_word_sorting_metrics,
    calculate_logical_deduction_metrics,
    calculate_causal_judgment_metrics
)
from src.metrics.utils import (
    extract_relevant_words,
    calculate_kendall_tau_distance
)
from src.dataset_manager import DatasetManager

# Create blueprint
api = Blueprint('api', __name__)

# Get configuration
config = get_config()

# Initialize dataset manager
dataset_manager = DatasetManager()

@api.route('/')
def home():
    return render_template('api_test.html')

@api.route('/api/pretest', methods=['POST'])
def pretest():
    try:
        dataset_type = request.json['dataset_type']
        show_details = request.json.get('show_details', False)
        
        if not config.GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

        client = Groq(api_key=config.GROQ_API_KEY)
        
        # Load dataset using dataset manager
        dataset = dataset_manager.load_dataset(dataset_type, mode="practice")
        if dataset is None:
            return jsonify({'error': 'Failed to load dataset'})

        expected_outputs, model_predictions, inputs_used, raw_predictions = [], [], [], []

        for i in range(len(dataset['inputs'])):
            full_input = dataset['inputs'][i]
            inputs_used.append(full_input)

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": request.json['system_prompt']},
                    {"role": "user", "content": full_input}
                ],
                model=config.MODEL_NAME,
                temperature=config.TEMPERATURE
            )
            model_response = chat_completion.choices[0].message.content.strip()
            
            if dataset_type == "word_sorting":
                sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
                model_predictions.append(sorted_words)
            else:
                model_predictions.append(model_response)
                
            expected_outputs.append(dataset['targets'][i])
            raw_predictions.append(model_response)

        # Calculate metrics based on dataset type
        response_data = get_metrics_response(
            dataset_type, 
            expected_outputs, 
            model_predictions, 
            request.json['system_prompt'],
            inputs_used,
            raw_predictions,
            show_details
        )
        
        return jsonify(response_data)

    except Exception as e:
        print("Error in pretest:", str(e))
        return jsonify({'error': str(e)})

@api.route('/api/test_prompt', methods=['POST'])
def test_prompt():
    try:
        dataset_type = request.json['dataset_type']
        num_examples = min(max(int(request.json.get('num_examples', 10)), 10), 100)

        if not config.GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

        client = Groq(api_key=config.GROQ_API_KEY)

        # Load dataset using dataset manager
        dataset = dataset_manager.load_dataset(dataset_type, mode="test", num_examples=num_examples)
        if dataset is None:
            return jsonify({'error': 'Failed to load dataset'})

        expected_outputs, model_predictions, inputs_used, raw_predictions = [], [], [], []

        for i in range(num_examples):
            full_input = dataset['inputs'][i]
            inputs_used.append(full_input)

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": request.json['system_prompt']},
                    {"role": "user", "content": full_input}
                ],
                model=config.MODEL_NAME,
                temperature=config.TEMPERATURE
            )
            model_response = chat_completion.choices[0].message.content.strip()
            
            if dataset_type == "word_sorting":
                sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
                model_predictions.append(sorted_words)
            else:
                model_predictions.append(model_response)
                
            expected_outputs.append(dataset['targets'][i])
            raw_predictions.append(model_response)

        # Calculate metrics based on dataset type
        response_data = get_metrics_response(
            dataset_type, 
            expected_outputs, 
            model_predictions, 
            request.json['system_prompt'],
            inputs_used,
            raw_predictions,
            True
        )
        
        return jsonify(response_data)

    except Exception as e:
        print("Error in test_prompt:", str(e))
        return jsonify({'error': str(e)})

def get_metrics_response(dataset_type, expected_outputs, model_predictions, system_prompt, 
                        inputs_used, raw_predictions, show_details):
    """Helper function to generate metrics response based on dataset type"""
    if dataset_type == "word_sorting":
        metrics = calculate_word_sorting_metrics(expected_outputs, model_predictions, system_prompt)
        examples = [
            {
                'input': inp,
                'expected': exp,
                'raw_prediction': raw,
                'processed_prediction': pred,
                'is_correct': exp.strip() == pred.strip(),
                'word_order_distance': calculate_kendall_tau_distance(exp.strip().split(), pred.strip().split())
            }
            for inp, exp, raw, pred in zip(inputs_used, expected_outputs, raw_predictions, model_predictions)
        ] if show_details else []
    else:
        metrics_func = calculate_logical_deduction_metrics if dataset_type == "logical_deduction" else calculate_causal_judgment_metrics
        metrics = metrics_func(expected_outputs, model_predictions, system_prompt)
        standardized_predictions = metrics.pop('standardized_outputs')
        examples = [
            {
                'input': inp,
                'expected': exp,
                'raw_prediction': raw,
                'processed_prediction': std_pred,
                'is_correct': exp.strip() == std_pred,
                'word_order_distance': None
            }
            for inp, exp, raw, std_pred in zip(inputs_used, expected_outputs, raw_predictions, standardized_predictions)
        ] if show_details else []

    return {
        'metrics': metrics,
        'examples': examples
    }