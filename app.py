from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from groq import Groq
from metrics import (
    extract_relevant_words,
    calculate_kendall_tau_distance,
    calculate_metrics,
    calculate_combined_score
)
from dataset_utils import download_word_sorting_dataset_by_length

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure template directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app.template_folder = template_dir
    
    # Get API key from environment variable
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    @app.route('/')
    def home():
        instructions = (
            "Use this interface to test prompts for sorting words in specific ways. "
            "You can start with Practice Mode using 8-word lists and proceed to Full Test Mode using 10-word lists. "
            "Enter your prompt and select the number of examples, then click the 'Run' button. "
            "For more accurate results, ensure that your prompt is specific and follows the intended test criteria."
            "Example input: 'cherry apple dragon baseball elephant'. Ideal sorted output: 'apple baseball cherry dragon elephant'."
        )
        return render_template('api_test.html', instructions=instructions)

    @app.route('/api/pretest', methods=['POST'])
    def pretest():
        try:
            system_prompt = request.json['system_prompt']
            show_details = request.json.get('show_details', False)

            if not GROQ_API_KEY:
                return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

            client = Groq(api_key=GROQ_API_KEY)
            dataset = download_word_sorting_dataset_by_length(word_length=8)
            if dataset is None:
                return jsonify({'error': 'Failed to load dataset'})

            expected_outputs, model_predictions, inputs_used, raw_predictions = [], [], [], []

            print("\nRunning pretest...")
            for i in range(len(dataset['inputs'])):
                full_input = dataset['inputs'][i]
                inputs_used.append(full_input)

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": full_input}],
                    model="llama3-8b-8192",
                    temperature=0
                )

                model_response = chat_completion.choices[0].message.content.strip()
                raw_predictions.append(model_response)
                sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
                expected_outputs.append(dataset['targets'][i])
                model_predictions.append(sorted_words)

            metrics = calculate_metrics(expected_outputs, model_predictions)
            print("Pretest Metrics Calculated:", metrics)  # Logging for debugging
            response_data = {
                'metrics': metrics,
                'message': 'Pretest completed! These results are from sorting 8-word lists.',
                'examples': [
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
            }
            
            return jsonify(response_data)

        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/api/test_prompt', methods=['POST'])
    def test_prompt():
        try:
            system_prompt = request.json['system_prompt']
            num_examples = min(max(int(request.json.get('num_examples', 50)), 5), 100)

            if not GROQ_API_KEY:
                return jsonify({'error': 'GROQ_API_KEY not found in environment variables'})

            client = Groq(api_key=GROQ_API_KEY)
            dataset = download_word_sorting_dataset_by_length(word_length=10)
            if dataset is None:
                return jsonify({'error': 'Failed to load dataset'})

            expected_outputs, model_predictions, inputs_used, raw_predictions = [], [], [], []

            print("\nTesting examples...")
            for i in range(num_examples):
                full_input = dataset['inputs'][i]
                inputs_used.append(full_input)

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": full_input}],
                    model="llama3-8b-8192",
                    temperature=0
                )

                model_response = chat_completion.choices[0].message.content.strip()
                raw_predictions.append(model_response)
                sorted_words = extract_relevant_words(model_response, dataset['targets'][i])
                expected_outputs.append(dataset['targets'][i])
                model_predictions.append(sorted_words)

            metrics = calculate_metrics(expected_outputs, model_predictions)
            print("Test Prompt Metrics Calculated:", metrics)  # Logging for debugging
            response_data = {
                'metrics': metrics,
                'examples': [
                    {
                        'input': inp,
                        'expected': exp,
                        'raw_prediction': raw,
                        'processed_prediction': pred,
                        'is_correct': exp.strip() == pred.strip(),
                        'word_order_distance': calculate_kendall_tau_distance(exp.strip().split(), pred.strip().split())
                    }
                    for inp, exp, raw, pred in zip(inputs_used, expected_outputs, raw_predictions, model_predictions)
                ]
            }
            
            return jsonify(response_data)

        except Exception as e:
            return jsonify({'error': str(e)})

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
