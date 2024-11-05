from flask import Blueprint, request, jsonify, render_template
from .metrics import calculate_metrics, calculate_logical_deduction_metrics
from .dataset_utils import (
    download_word_sorting_dataset_by_length,
    load_logical_deduction_five_objects,
    load_logical_deduction_seven_objects
)

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return render_template('api_test.html')

@api.route('/api/pretest', methods=['POST'])
def pretest():
    try:
        dataset_type = request.json.get('dataset_type')
        show_details = request.json.get('show_details', False)

        # Load dataset based on selected type
        if dataset_type == "word_sorting":
            dataset = download_word_sorting_dataset_by_length(word_length=8)
        elif dataset_type == "logical_deduction":
            dataset = load_logical_deduction_five_objects(num_examples=10)
        else:
            return jsonify({'error': 'Invalid dataset type'}), 400

        # Perform other processing with `dataset`
        # e.g., calculate metrics, process examples

        return jsonify({"message": "Pretest complete", "dataset_type": dataset_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/test_prompt', methods=['POST'])
def test_prompt():
    try:
        dataset_type = request.json.get('dataset_type')
        num_examples = min(max(int(request.json.get('num_examples', 50)), 10), 100)

        # Load dataset based on selected type
        if dataset_type == "word_sorting":
            dataset = download_word_sorting_dataset_by_length(word_length=10)
        elif dataset_type == "logical_deduction":
            dataset = load_logical_deduction_seven_objects(num_examples=num_examples)
        else:
            return jsonify({'error': 'Invalid dataset type'}), 400

        # Perform other processing with `dataset`
        # e.g., calculate metrics, process examples

        return jsonify({"message": "Test prompt complete", "dataset_type": dataset_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
