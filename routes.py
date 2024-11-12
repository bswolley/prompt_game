from flask import Blueprint, request, jsonify, render_template
from groq import Groq
import os
from metrics import (
    extract_relevant_words,
    calculate_kendall_tau_distance,
    calculate_metrics,
    calculate_logical_deduction_metrics,
    calculate_causal_judgment_metrics
)
from dataset_utils import (
    load_word_sorting_dataset_by_length,
    load_logical_deduction_five_objects,
    load_logical_deduction_three_objects,
    load_causal_judgement
)

api = Blueprint('api', __name__)

@api.route('/')
def home():
    instructions = {
        'general': (
            "Use this interface to test prompts for different types of tasks. "
            "You can start with Practice Mode and proceed to Full Test Mode. "
            "Enter your prompt and select the number of examples, then click the 'Run' button."
        ),
        'word_sorting': (
            "For Word Sorting: Create prompts that sort words in alphabetical order.\n"
            "Example input: 'cherry apple dragon baseball elephant'\n"
            "Expected output: 'apple baseball cherry dragon elephant'"
        ),
        'logical_deduction': (
            "For Logical Deduction: Create prompts that solve logical puzzles.\n"
            "Answer should be in format (A), (B), etc.\n"
            "Practice Mode uses 5-object puzzles, Full Test uses 3-object puzzles."
        ),
        'causal_judgement': (
            "For Causal Judgement: Create prompts that assess judgement situations.\n"
            "Answer should be in yes/no format.\n"
            "Practice Mode uses 10 fixed examples, Full Test uses random examples from remaining dataset."
        )
    }
    return render_template('api_test.html', instructions=instructions)

@api.route('/api/pretest', methods=['POST'])
def pretest():
    try:
        dataset_type = request.json['dataset_type']
        show_details = request.json.get('show_details', False)
        
        GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

        client = Groq(api_key=GROQ_API_KEY)
        
        # Load appropriate dataset based on type
        if dataset_type == "word_sorting":
            dataset = load_word_sorting_dataset_by_length(word_length=8)
        elif dataset_type == "logical_deduction":
            dataset = load_logical_deduction_five_objects()
        elif dataset_type == "causal_judgement":
            dataset = load_causal_judgement(is_pretest=True)
        else:
            return jsonify({'error': 'Invalid dataset type'})

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
                model="llama3-70b-8192",
                temperature=0
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
        if dataset_type == "word_sorting":
            metrics = calculate_metrics(expected_outputs, model_predictions, request.json['system_prompt'])
            response_data = create_word_sorting_response(
                metrics, inputs_used, expected_outputs, raw_predictions, 
                model_predictions, show_details
            )
        else:
            response_data = create_logical_causal_response(
                dataset_type, expected_outputs, model_predictions, 
                inputs_used, raw_predictions, request.json['system_prompt'],
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

        GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

        client = Groq(api_key=GROQ_API_KEY)

        # Load appropriate dataset based on type
        dataset = load_dataset(dataset_type, num_examples)
        if dataset is None:
            return jsonify({'error': 'Failed to load dataset'})

        expected_outputs, model_predictions, inputs_used, raw_predictions = process_examples(
            client, dataset, dataset_type, request.json['system_prompt'], num_examples
        )

        # Calculate metrics based on dataset type
        if dataset_type == "word_sorting":
            metrics = calculate_metrics(expected_outputs, model_predictions, request.json['system_prompt'])
            response_data = create_word_sorting_response(
                metrics, inputs_used, expected_outputs, raw_predictions, 
                model_predictions, True
            )
        else:
            response_data = create_logical_causal_response(
                dataset_type, expected_outputs, model_predictions,
                inputs_used, raw_predictions, request.json['system_prompt'],
                True
            )
        
        return jsonify(response_data)

    except Exception as e:
        print("Error in test_prompt:", str(e))
        return jsonify({'error': str(e)})

# Helper functions
def load_dataset(dataset_type, num_examples):
    if dataset_type == "word_sorting":
        return load_word_sorting_dataset_by_length(word_length=10, num_examples=num_examples)
    elif dataset_type == "logical_deduction":
        return load_logical_deduction_three_objects(num_examples=num_examples)
    elif dataset_type == "causal_judgement":
        return load_causal_judgement(is_pretest=False, num_examples=num_examples)
    else:
        raise ValueError('Invalid dataset type')

def process_examples(client, dataset, dataset_type, system_prompt, num_examples):
    expected_outputs, model_predictions = [], []
    inputs_used, raw_predictions = [], []

    for i in range(num_examples):
        full_input = dataset['inputs'][i]
        inputs_used.append(full_input)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_input}
            ],
            model="llama3-70b-8192",
            temperature=0
        )
        model_response = chat_completion.choices[0].message.content.strip()
        
        if dataset_type == "word_sorting":
            sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
            model_predictions.append(sorted_words)
        else:
            model_predictions.append(model_response)
            
        expected_outputs.append(dataset['targets'][i])
        raw_predictions.append(model_response)

    return expected_outputs, model_predictions, inputs_used, raw_predictions

def create_word_sorting_response(metrics, inputs, expected, raw, predictions, show_details):
    response_data = {
        'metrics': metrics,
        'examples': [
            {
                'input': inp,
                'expected': exp,
                'raw_prediction': raw_pred,
                'processed_prediction': pred,
                'is_correct': exp.strip() == pred.strip(),
                'word_order_distance': calculate_kendall_tau_distance(
                    exp.strip().split(), pred.strip().split()
                )
            }
            for inp, exp, raw_pred, pred in zip(inputs, expected, raw, predictions)
        ] if show_details else []
    }
    return response_data

def create_logical_causal_response(dataset_type, expected, predictions, inputs, raw, system_prompt, show_details):
    metrics_func = (
        calculate_logical_deduction_metrics 
        if dataset_type == "logical_deduction" 
        else calculate_causal_judgment_metrics
    )
    metrics = metrics_func(expected, predictions, system_prompt)
    standardized_predictions = metrics.pop('standardized_outputs')
    
    response_data = {
        'metrics': metrics,
        'examples': [
            {
                'input': inp,
                'expected': exp,
                'raw_prediction': raw_pred,
                'processed_prediction': std_pred,
                'is_correct': exp.strip() == std_pred,
                'word_order_distance': None
            }
            for inp, exp, raw_pred, std_pred in zip(
                inputs, expected, raw, standardized_predictions
            )
        ] if show_details else []
    }
    return response_data