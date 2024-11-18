from flask import Flask, Blueprint, request, jsonify, render_template, send_from_directory, current_app
import requests
from groq import Groq
import datetime
from flask.cli import click
from pathlib import Path 
import json
import os
from src.config import get_config
from src.metrics import (
    calculate_word_sorting_metrics,
    calculate_logical_deduction_metrics,     
    calculate_causal_judgment_metrics,
    calculate_summarization_metrics
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

def float_convert(value):
    if hasattr(value, 'item'):  # Check if it's a numpy type
        return value.item()
    return float(value) if value is not None else 0.0

@api.route('/')
def home():
    return render_template('api_test.html')

@api.route('/config/datasets.json', methods=['GET'])
def serve_datasets_json():
    # Adjust path to match your project's structure
    config_directory = os.path.join(os.getcwd(), 'config')
    return send_from_directory(config_directory, 'datasets.json')

# Add to your existing routes file where other routes are
@api.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')

@api.route('/api/leaderboard/<dataset_type>', methods=['POST'])
def add_leaderboard_entry(dataset_type):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        print("Debug - Full data received:", data)  # Add this debug line
        
        leaderboard_dir = Path("leaderboards")
        leaderboard_dir.mkdir(exist_ok=True)
        path = leaderboard_dir / f"{dataset_type}.json"
        
        entries = []
        if path.exists():
            with open(path) as f:
                entries = json.load(f)
        
        metrics = data['metrics']
        
        # Base entry with common fields
        new_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'name': data.get('name', 'Anonymous'),
            'prompt_length': metrics.get('prompt_length_chars', metrics.get('prompt_length', 0)),
        }

        # Add dataset-specific metrics
        if dataset_type == "word_sorting":
            efficiency = float_convert(metrics.get('efficiency_modifier', 0)) * 100  # Convert to percentage
            print(f"Debug - Converting efficiency: {metrics.get('efficiency_modifier', 0)} to {efficiency}%")  # Debug line
            new_entry.update({
                'score': float_convert(metrics.get('combined_score', 0)),
                'accuracy': float_convert(metrics.get('accuracy', 0)),
                'word_accuracy': float_convert(metrics.get('word_accuracy', 0)),
                'efficiency': efficiency

            })
        
        elif dataset_type == "text_summarization":
            new_entry.update({
                'score': float(metrics.get('final_score', 0)),
                'similarity': float(metrics.get('similarity', 0)),
                'length_penalty_avg': float(metrics.get('length_penalty_avg', 0)),
                'prompt_efficiency': float(metrics.get('prompt_efficiency', 0))
            })
        
        elif dataset_type == "causal_judgement":
            new_entry.update({
                'score': float(metrics.get('final_score', 0)),
                'accuracy': float(metrics.get('accuracy', 0)),
                'base_accuracy': float(metrics.get('base_accuracy', 0)),
                'efficiency': float(metrics.get('efficiency', 0))
            })

        print("Debug - New entry after processing:", new_entry)  # Add this debug line

        # Don't remove existing entries if the list is less than 20
        if len(entries) < 20:
            entries.append(new_entry)
        else:
            min_score = min(entries, key=lambda x: x['score'])
            if new_entry['score'] > min_score['score']:
                entries.remove(min_score)
                entries.append(new_entry)

        # Sort by score in descending order
        entries = sorted(entries, key=lambda x: x['score'], reverse=True)[:20]
        
        with open(path, 'w') as f:
            json.dump(entries, f, indent=2)

        return jsonify({'success': True})
        
    except Exception as e:
        print("Error in add_leaderboard_entry:", str(e))
        print("Full error details:", e.__dict__)  # Add this debug line
        return jsonify({'error': str(e)}), 400
    
@api.route('/api/leaderboard/<dataset_type>', methods=['GET'])
def get_leaderboard(dataset_type):
    try:
        path = Path("leaderboards") / f"{dataset_type}.json"
        if path.exists():
            with open(path) as f:
                return jsonify(json.load(f))
        return jsonify([])
    except Exception as e:
        print(f"Error getting leaderboard: {str(e)}")
        return jsonify([])


@api.route('/api/pretest', methods=['POST'])
def pretest(): 
    try:
        dataset_type = request.json['dataset_type']
        show_details = request.json.get('show_details', False)
        
        # Add detailed debugging
        print("DEBUG: Checking GROQ key status...")
        print(f"DEBUG: Key exists: {bool(config.GROQ_API_KEY)}")
        if config.GROQ_API_KEY:
            print(f"DEBUG: Key length: {len(config.GROQ_API_KEY)}")
            print(f"DEBUG: Key starts with: {config.GROQ_API_KEY[:4]}...")
        
        if not config.GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

        print("DEBUG: About to create Groq client...")
        client = Groq(api_key=config.GROQ_API_KEY)
        print("DEBUG: Groq client created successfully")
        
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
            raw_predictions.append(model_response)

            if dataset_type == "word_sorting":
                sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
                model_predictions.append(sorted_words)
            else:
                model_predictions.append(model_response)
                
            expected_outputs.append(dataset['targets'][i])

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
       submitted_name = request.json.get('name', 'Anonymous')  # Changed to match frontend
       
       print(f"Debug - Received name: {submitted_name}")

       if not config.GROQ_API_KEY:
           return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

       client = Groq(api_key=config.GROQ_API_KEY)
       
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
           raw_predictions.append(model_response)
           
           if dataset_type == "word_sorting":
               sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
               model_predictions.append(sorted_words)
           else:
               model_predictions.append(model_response)
               
           expected_outputs.append(dataset['targets'][i])

       response_data = get_metrics_response(
           dataset_type, 
           expected_outputs, 
           model_predictions, 
           request.json['system_prompt'],
           inputs_used,
           raw_predictions,
           True
       )

       print("Debug - Metrics data:", response_data['metrics'])
       
       # Save to leaderboard
       try:
           leaderboard_entry = {
               'name': submitted_name,  # Use the submitted name
               'metrics': response_data['metrics']
           }
           print("Debug - Leaderboard entry:", leaderboard_entry)
           
           result = current_app.test_client().post(
               f'/api/leaderboard/{dataset_type}',
               json=leaderboard_entry
           )
           print("Debug - Leaderboard save result:", result.data)
           
       except Exception as e:
           print("Debug - Error saving to leaderboard:", str(e))

       return jsonify(response_data)

   except Exception as e:
       print("Error in test_prompt:", str(e))
       return jsonify({'error': str(e)})

@api.app_template_filter()
def get_metrics_response(dataset_type, expected_outputs, model_predictions, system_prompt, 
                        inputs_used, raw_predictions, show_details):
    """Helper function to generate metrics response based on dataset type"""
    try:
        if dataset_type == "word_sorting":
            metrics = calculate_word_sorting_metrics(expected_outputs, model_predictions, system_prompt)
            examples = [
                {
                    'input': inp,
                    'expected': exp,
                    'raw_prediction': raw,
                    'processed_prediction': pred,
                    'is_correct': metrics['individual_scores'][i]['is_correct'],
                    'word_order_distance': metrics['individual_scores'][i]['word_order_distance'],
                    'scores': {
                        'final_score': metrics['individual_scores'][i]['final_score'],
                        'word_accuracy': metrics['individual_scores'][i]['word_accuracy'],
                        'word_order_distance': metrics['individual_scores'][i]['word_order_distance'],
                        'efficiency': round(metrics['efficiency_modifier'] * 100, 2)
                    }
                }
                for i, (inp, exp, raw, pred) in enumerate(zip(inputs_used, expected_outputs, raw_predictions, model_predictions))
            ] if show_details else []

        elif dataset_type == "logical_deduction":
            metrics = calculate_logical_deduction_metrics(expected_outputs, model_predictions, system_prompt)
            examples = [
                {
                    'input': inp,
                    'expected': exp,
                    'raw_prediction': raw,
                    'processed_prediction': std_pred,
                    'is_correct': exp.strip() == std_pred,
                }
                for inp, exp, raw, std_pred in zip(inputs_used, expected_outputs, raw_predictions, metrics['standardized_outputs'])
            ] if show_details else []
        
        elif dataset_type == "causal_judgement":
            metrics = calculate_causal_judgment_metrics(expected_outputs, model_predictions, system_prompt)
            standardized_predictions = metrics.pop('standardized_outputs', model_predictions)
            examples = [
                {
                    'input': inp,
                    'expected': exp,
                    'raw_prediction': raw,
                    'processed_prediction': std_pred,
                    'is_correct': metrics['individual_scores'][i]['is_correct'],
                    'scores': {
                        'final_score': metrics['individual_scores'][i]['final_score'],
                        'base_accuracy': metrics['individual_scores'][i]['base_accuracy'],
                        'efficiency': metrics['individual_scores'][i]['efficiency']
                    }
                }
                for i, (inp, exp, raw, std_pred) in enumerate(zip(inputs_used, expected_outputs, raw_predictions, standardized_predictions))
            ] if show_details else []
        
        elif dataset_type == "text_summarization":
            print("Processing text summarization metrics...")
            metrics = calculate_summarization_metrics(expected_outputs, model_predictions, system_prompt)
            print("Metrics calculated:", metrics)
            
            examples = [
                {
                    'input': inp,
                    'expected': exp,
                    'raw_prediction': raw,
                    'processed_prediction': model_pred,
                    'is_correct': metrics['individual_scores'][i]['similarity'] >= 70.0,
                    'similarity_score': metrics['individual_scores'][i]['similarity'],
                    'actual_length': metrics['individual_scores'][i]['actual_length'],
                    'expected_length': metrics['individual_scores'][i]['expected_length'],
                    'scores': {
                        'similarity': metrics['individual_scores'][i]['similarity'],
                        'length_penalty': metrics['individual_scores'][i]['length_penalty']
                    }
                }
                for i, (inp, exp, raw, model_pred) in enumerate(zip(inputs_used, expected_outputs, raw_predictions, model_predictions))
            ] if show_details else []
        
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")

        return {
            'metrics': metrics,
            'examples': examples
        }
    
    except Exception as e:
        print(f"Error in get_metrics_response: {str(e)}")
        raise

@api.cli.command('clear-leaderboard')
@click.argument('dataset_type', required=False)
def clear_leaderboard(dataset_type=None):
    """Clear the leaderboard for a specific dataset type or all leaderboards."""
    leaderboard_dir = Path("leaderboards")
    
    if dataset_type:
        path = leaderboard_dir / f"{dataset_type}.json"
        if path.exists():
            with open(path, 'w') as f:
                json.dump([], f)
            click.echo(f"Cleared leaderboard for {dataset_type}")
        else:
            click.echo(f"No leaderboard found for {dataset_type}")
    else:
        # Clear all leaderboards
        for path in leaderboard_dir.glob('*.json'):
            with open(path, 'w') as f:
                json.dump([], f)
        click.echo("Cleared all leaderboards")