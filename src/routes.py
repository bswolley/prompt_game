from flask import Flask, Blueprint, request, jsonify, render_template, send_from_directory, current_app
import requests
from .models import db, LeaderboardEntry
from groq import Groq
import datetime
from flask.cli import click
from pathlib import Path 
import random
import json
import os
from src.config import get_config
from src.metrics import (
    calculate_word_sorting_metrics,
    calculate_logical_deduction_metrics,     
    calculate_causal_judgment_metrics,
    calculate_summarization_metrics,
    calculate_translation_metrics,
    calculate_complex_metrics
)
from src.metrics.utils import (
    extract_relevant_words,
    calculate_kendall_tau_distance
)
from src.dataset_manager import DatasetManager
# Create blueprint
api = Blueprint('api', __name__)

# Add this near the top with other constants
IS_PRODUCTION = os.environ.get('GAE_ENV', '').startswith('standard')

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
    config_directory = os.path.join(os.getcwd(), 'config')
    return send_from_directory(config_directory, 'datasets.json')

@api.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')

@api.route('/api/leaderboard/<dataset_type>', methods=['POST'])
def add_leaderboard_entry(dataset_type):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        metrics = data['metrics']
        
        # Create new entry
        new_entry = LeaderboardEntry(
            dataset_type=dataset_type,
            name=data.get('name', 'Anonymous'),
            prompt_length=metrics.get('prompt_length_chars', metrics.get('prompt_length', 0)),
            is_production=IS_PRODUCTION,  # Keep this to differentiate environments
            system_prompt=data.get('system_prompt'),
            raw_predictions=data.get('raw_predictions'),
            inputs_used=data.get('inputs_used')
        )

        if dataset_type == "word_sorting":
            efficiency = float(metrics.get('efficiency_modifier', 0)) * 100
            new_entry.score = float(metrics.get('combined_score', 0))
            new_entry.accuracy = float(metrics.get('accuracy', 0))
            new_entry.word_accuracy = float(metrics.get('word_accuracy', 0))
            new_entry.efficiency = efficiency

        elif dataset_type == "text_summarization":
            new_entry.score = float(metrics.get('final_score', 0))
            new_entry.similarity = float(metrics.get('similarity', 0))
            new_entry.length_penalty_avg = float(metrics.get('length_penalty_avg', 0))
            new_entry.prompt_efficiency = float(metrics.get('prompt_efficiency', 0))

        elif dataset_type == "causal_judgement":
            new_entry.score = float(metrics.get('final_score', 0))
            new_entry.accuracy = float(metrics.get('accuracy', 0))
            new_entry.base_accuracy = float(metrics.get('base_accuracy', 0))
            new_entry.efficiency = float(metrics.get('efficiency', 0))

        elif dataset_type == "translation_task":
            new_entry.score = float(metrics.get('final_score', 0))
            new_entry.semantic_similarity = float(metrics.get('semantic_similarity', 0))
            new_entry.language_quality = float(metrics.get('language_quality', 0))
            new_entry.efficiency = float(metrics.get('efficiency', 0))
            new_entry.target_language = request.json.get('target_language', '')

        

        db.session.add(new_entry)
        db.session.commit()
        print(f"Added entry ID: {new_entry.id} for {dataset_type}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        print("Error in add_leaderboard_entry:", str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/api/leaderboard/<dataset_type>', methods=['GET'])
def get_leaderboard(dataset_type):
    try:
        entries = LeaderboardEntry.query.filter_by(
            dataset_type=dataset_type,
            is_production=IS_PRODUCTION
        ).order_by(
            LeaderboardEntry.score.desc()
        ).limit(20).all()
        
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        print(f"Error getting leaderboard: {str(e)}")
        return jsonify([])

@api.route('/api/complex_practice', methods=['GET'])
def get_complex_practice_data():
    try:
        # Path to the JSON file
        json_path = os.path.join(os.getcwd(), 'data', 'complex_practice.json')
        
        # Load the data from the file
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        print(f"Error loading complex practice data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/api/pretest', methods=['POST'])
def pretest():
    try:
        dataset_type = request.json['dataset_type']
        show_details = request.json.get('show_details', False)
        target_language = request.json.get('target_language', None)
        system_prompt = request.json.get('system_prompt', '')

        # Load dataset
        dataset = dataset_manager.load_dataset(dataset_type, mode="practice")
        if dataset is None:
            return jsonify({'error': 'Failed to load dataset'}), 400

        # Check if the API key is available
        if not config.GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found'}), 400

        # Initialize the Groq client
        client = Groq(api_key=config.GROQ_API_KEY)

        # Handle "complex_transformation" dataset type
        if dataset_type == "complex_transformation":
            if 'examples' not in dataset:
                return jsonify({'error': 'Invalid complex transformation dataset format'}), 400

            inputs = dataset['examples']
            turn = request.json.get('turn', 1)
            previous_outputs = request.json.get('previous_outputs', [])
            
            print(f"DEBUG - Complex turn {turn} with previous outputs: {previous_outputs}")

            try:
                # If it's Turn 3, process Turn 2 output with Turn 3's prompt
                if turn == 3:
                    # Combine Turn 2 output and Turn 3's prompt
                    combined_input = f"{previous_outputs[-1]}\n\n{system_prompt}"
                    print(f"DEBUG - Combined input for Turn 3: {combined_input}")

                    # Send combined input to the model
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": combined_input}
                        ],
                        model=config.MODEL_NAME,
                        temperature=config.TEMPERATURE
                    )

                    # Get model response
                    model_response = chat_completion.choices[0].message.content.strip()
                    print(f"DEBUG - Turn 3 model response: {model_response}")

                    # Evaluate the final output for Turn 3
                    print(f"DEBUG - Evaluating Turn 3 output for task: {inputs[0]['task_description']}")
                    metrics = calculate_complex_metrics(
                        task_descriptions=[inputs[0]['task_description']],
                        user_outputs=[model_response],
                        reference_solutions=[inputs[0]['evaluation_reference']],
                        system_prompt=system_prompt,
                        inputs=[{
                            'task_description': inputs[0]['task_description'],
                            'evaluation_guide': inputs[0]['evaluation_guide'],
                            'evaluation_reference': inputs[0]['evaluation_reference']
                        }]
                    )
                    
                    print(f"DEBUG - Calculated metrics for Turn 3: {metrics}")

                    # Get explanation from individual_scores
                    explanation = ''
                    if metrics.get('individual_scores') and len(metrics['individual_scores']) > 0:
                        explanation = metrics['individual_scores'][0].get('explanation', '')
                    
                    # Prepare response data
                    response_data = {
                        'metrics': metrics,
                        'examples': [{
                            'task_description': inputs[0]['task_description'],
                            'reference_solution': inputs[0]['evaluation_reference'],
                            'raw_prediction': model_response,
                            'processed_prediction': model_response,
                            'rule_accuracy': metrics.get('rule_accuracy', 0),
                            'completeness': metrics.get('completeness', 0),
                            'format_score': metrics.get('format_score', 0),
                            'explanation': explanation
                        }]
                    }
                    
                    print(f"DEBUG - Sending response data for Turn 3: {response_data}")
                    return jsonify(response_data)

                # For Turns 1 and 2, get model response
                messages = [{"role": "system", "content": system_prompt}]
                if turn > 1 and previous_outputs:
                    messages.extend([
                        {"role": "assistant", "content": previous_outputs[-1]},
                        {"role": "user", "content": system_prompt}
                    ])

                print(f"DEBUG - Sending messages to GROQ for Turn {turn}: {messages}")

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=config.MODEL_NAME,
                    temperature=config.TEMPERATURE
                )
                
                model_response = chat_completion.choices[0].message.content.strip()
                print(f"DEBUG - Got model response for Turn {turn}: {model_response[:100]}...")
                
                if not model_response:
                    return jsonify({'error': 'Empty response from model'}), 400

                return jsonify({
                    'examples': [{
                        'task_description': inputs[0]['task_description'],
                        'display_reference': inputs[0]['evaluation_reference'],
                        'raw_prediction': model_response,
                        'processed_prediction': model_response
                    }]
                })
                    
            except Exception as e:
                print(f"DEBUG - Error in complex transformation: {str(e)}")
                return jsonify({'error': str(e)}), 400

        # Handle non-complex tasks
        inputs_used, raw_predictions, model_predictions = [], [], []
        expected_outputs = []

        if dataset_type == "translation_task":
            if 'examples' not in dataset:
                return jsonify({'error': 'Invalid translation dataset format'}), 400
            inputs = [example['input'] for example in dataset['examples']]
            expected_outputs = [example['translations'][target_language]
                                for example in dataset['examples']]
        else:
            if 'inputs' not in dataset or 'targets' not in dataset:
                return jsonify({'error': 'Invalid dataset format'}), 400
            inputs = dataset['inputs']
            expected_outputs = dataset['targets']

        # Process each input
        for i, full_input in enumerate(inputs):
            try:
                messages = [{"role": "system", "content": system_prompt}]
                
                input_content = full_input['input'] if isinstance(full_input, dict) else full_input
                messages.append({"role": "user", "content": input_content})

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=config.MODEL_NAME,
                    temperature=config.TEMPERATURE
                )
                model_response = chat_completion.choices[0].message.content.strip()
                raw_predictions.append(model_response)
                model_predictions.append(model_response)
                inputs_used.append(full_input)
            except Exception as e:
                print(f"Error in chat completion {i}: {str(e)}")
                raw_predictions.append("")
                model_predictions.append("")

        # Get metrics response
        response_data = get_metrics_response(
            dataset_type=dataset_type,
            expected_outputs=expected_outputs,
            model_predictions=model_predictions,
            system_prompt=system_prompt,
            inputs_used=inputs_used,
            raw_predictions=raw_predictions,
            show_details=show_details
        )

        return jsonify(response_data)

    except Exception as e:
        print("Error in pretest:", str(e))
        return jsonify({'error': str(e)}), 400

@api.route('/api/complex_test', methods=['GET'])
def get_complex_test_data():
    try:
        # Path to the test JSON file
        json_path = os.path.join(os.getcwd(), 'data', 'complex_test.json')
        
        # Load the data from the file
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        print(f"Error loading complex test data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/api/test_prompt', methods=['POST'])
def test_prompt():
    try:
        dataset_type = request.json['dataset_type']
        submitted_name = request.json.get('name', 'Anonymous')
        system_prompt = request.json.get('system_prompt')
        target_language = request.json.get('target_language')
        turn = request.json.get('turn', 1)
        previous_outputs = request.json.get('previous_outputs', [])
        
        print(f"Debug - Received name: {submitted_name}")
        print(f"Debug - Turn: {turn}")
        print(f"Debug - Previous outputs: {previous_outputs}")

        if not config.GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found'}), 400

        # Initialize the Groq client
        client = Groq(api_key=config.GROQ_API_KEY)

        # Load dataset using dataset manager with test mode
        dataset = dataset_manager.load_dataset(dataset_type, mode="test")
        if dataset is None:
            return jsonify({'error': 'Failed to load dataset'}), 400

        # Handle "complex_transformation" dataset type
        if dataset_type == "complex_transformation":
            if 'examples' not in dataset:
                return jsonify({'error': 'Invalid complex transformation dataset format'}), 400

            example = dataset['examples'][0]  # We know there's exactly one example from dataset manager
            
            try:
                # If it's Turn 3, process Turn 2 output with Turn 3's prompt
                if turn == 3:
                    # Combine Turn 2 output and Turn 3's prompt
                    combined_input = f"{previous_outputs[-1]}\n\n{system_prompt}"
                    print(f"DEBUG - Combined input for Turn 3: {combined_input}")

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": combined_input}
                        ],
                        model=config.MODEL_NAME,
                        temperature=config.TEMPERATURE
                    )

                    model_response = chat_completion.choices[0].message.content.strip()
                    print(f"DEBUG - Turn 3 model response: {model_response}")

                    # Evaluate final output using full evaluation reference
                    metrics = calculate_complex_metrics(
                        task_descriptions=[example['task_description']],
                        user_outputs=[model_response],
                        reference_solutions=[example['evaluation_reference']],
                        system_prompt=system_prompt,
                        inputs=[{
                            'task_description': example['task_description'],
                            'evaluation_guide': example['evaluation_guide'],
                            'evaluation_reference': example['evaluation_reference']
                        }]
                    )

                    # Save to leaderboard with complete information
                    leaderboard_entry = {
                        'name': submitted_name,
                        'metrics': metrics,
                        'system_prompt': system_prompt,
                        'raw_predictions': [model_response],
                        'inputs_used': [{
                            'task_description': example['task_description'],
                            'evaluation_guide': example['evaluation_guide'],
                            'evaluation_reference': example['evaluation_reference']
                        }]
                    }
                    
                    result = current_app.test_client().post(
                        f'/api/leaderboard/{dataset_type}',
                        json=leaderboard_entry
                    )
                    print("Debug - Leaderboard save result:", result.data)

                    # Return final results with complete information
                    return jsonify({
                        'metrics': metrics,
                        'examples': [{
                            'task_description': example['task_description'],
                            'reference_solution': example['evaluation_reference'],
                            'raw_prediction': model_response,
                            'processed_prediction': model_response,
                            'explanation': metrics['individual_scores'][0].get('explanation', '')
                        }]
                    })

                # For Turns 1 and 2, get model response
                messages = [{"role": "system", "content": system_prompt}]
                if turn > 1 and previous_outputs:
                    messages.extend([
                        {"role": "assistant", "content": previous_outputs[-1]},
                        {"role": "user", "content": system_prompt}
                    ])

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=config.MODEL_NAME,
                    temperature=config.TEMPERATURE
                )
                
                model_response = chat_completion.choices[0].message.content.strip()
                print(f"DEBUG - Got model response for Turn {turn}: {model_response[:100]}...")
                
                # For turns 1 & 2, return display_reference (shorter version)
                return jsonify({
                    'examples': [{
                        'task_description': example['task_description'],
                        'display_reference': example['display_reference'],
                        'raw_prediction': model_response,
                        'processed_prediction': model_response
                    }]
                })
                    
            except Exception as e:
                print(f"DEBUG - Error in complex transformation: {str(e)}")
                return jsonify({'error': str(e)}), 400

        # Handle non-complex tasks
        NUM_EXAMPLES = 10
        expected_outputs, model_predictions, inputs_used, raw_predictions = [], [], [], []

        if dataset_type == 'translation_task':
            all_examples = dataset['examples']
            selected_indices = random.sample(range(len(all_examples)), NUM_EXAMPLES)
            
            for idx in selected_indices:
                example = all_examples[idx]
                inputs_used.append(example['input'])
                expected_outputs.append(example['translations'][target_language])
        else:
            total_examples = len(dataset['inputs'])
            selected_indices = random.sample(range(total_examples), NUM_EXAMPLES)
            
            for idx in selected_indices:
                inputs_used.append(dataset['inputs'][idx])
                expected_outputs.append(dataset['targets'][idx])

        # Process each input for non-complex tasks
        for i, full_input in enumerate(inputs_used):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_input}
                    ],
                    model=config.MODEL_NAME,
                    temperature=config.TEMPERATURE
                )
                model_response = chat_completion.choices[0].message.content.strip()
                raw_predictions.append(model_response)
                model_predictions.append(model_response)
            except Exception as e:
                print(f"Error in chat completion {i}: {str(e)}")
                raw_predictions.append("")
                model_predictions.append("")

        # Get metrics response for non-complex tasks
        response_data = get_metrics_response(
            dataset_type=dataset_type,
            expected_outputs=expected_outputs,
            model_predictions=model_predictions,
            system_prompt=system_prompt,
            inputs_used=inputs_used,
            raw_predictions=raw_predictions,
            show_details=True
        )

        if dataset_type == 'translation_task':
            response_data['metrics']['target_language'] = target_language

        # Save to leaderboard
        try:
            leaderboard_entry = {
                'name': submitted_name,
                'metrics': response_data['metrics'],
                'system_prompt': system_prompt,
                'raw_predictions': raw_predictions,
                'inputs_used': inputs_used,
                'target_language': target_language if dataset_type == 'translation_task' else None
            }
            
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
        return jsonify({'error': str(e)}), 400

def get_metrics_response(dataset_type, expected_outputs, model_predictions, system_prompt,
                       inputs_used, raw_predictions, show_details, task_descriptions=None):
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
           metrics = calculate_summarization_metrics(expected_outputs, model_predictions, system_prompt)
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

       elif dataset_type == "translation_task":
           metrics = calculate_translation_metrics(
               source_texts=inputs_used,
               model_translations=model_predictions,
               reference_translations=expected_outputs,
               system_prompt=system_prompt,
               language=request.json.get('target_language')
           )
           
           examples = [
               {
                   'input': inp,
                   'expected': exp,
                   'raw_prediction': raw,
                   'processed_prediction': pred,
                   'final_score': score.get('final_score', 0),
                   'semantic_score': score.get('semantic_score', 0),
                   'quality_score': score.get('quality_score', 0),
                   'efficiency': score.get('efficiency', 0),
                   'explanation': score.get('explanation', '')
               }
               for inp, exp, raw, pred, score in zip(
                   inputs_used,
                   expected_outputs,
                   raw_predictions,
                   model_predictions,
                   metrics.get('individual_scores', [])
               )
           ] if show_details else []

       elif dataset_type == "complex_transformation":
           reference_solutions = [ex['evaluation_reference'] for ex in inputs_used]  # ADD THIS LINE
           
           metrics = calculate_complex_metrics(
               task_descriptions=task_descriptions,
               user_outputs=model_predictions,
               reference_solutions=reference_solutions,  # NOW IT EXISTS
               system_prompt=system_prompt,
               inputs=inputs_used  
           )

           examples = [
               {
                   'task_description': inp['task_description'],
                   'reference_solution': inp['evaluation_reference'],
                   'raw_prediction': raw,
                   'processed_prediction': raw,
                   'raw_score': metrics['individual_scores'][i]['raw_score'],
                   'adjusted_score': metrics['individual_scores'][i]['adjusted_score'],
                   'explanation': metrics['individual_scores'][i]['explanation'],
                   'rule_accuracy': metrics['individual_scores'][i]['rule_accuracy'],
                   'completeness': metrics['individual_scores'][i]['completeness'],
                   'format_score': metrics['individual_scores'][i]['format_score']
               }
               for i, (inp, raw) in enumerate(zip(inputs_used, raw_predictions))
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