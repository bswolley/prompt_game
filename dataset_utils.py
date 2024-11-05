import json
import requests
from datasets import Dataset

def download_word_sorting_dataset_by_length(word_length=8):
    """
    Download BIG-bench word sorting dataset.
    Args:
        word_length: Number of words in each example
    """
    url = "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/word_sorting/task.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)

        # Filter for specified word length examples
        examples = data['examples']
        filtered_examples = [ex for ex in examples if len(ex['input'].split()) == word_length]

        if not filtered_examples:
            raise ValueError(f"No {word_length}-word examples found in the dataset")

        # For practice (8 words), use 10 examples
        # For full test (10 words), use up to 100 examples
        max_examples = 10 if word_length == 8 else 100
        selected_examples = filtered_examples[:max_examples]

        inputs = [example['input'] for example in selected_examples]
        targets = [example['target'] for example in selected_examples]

        print(f"Found {len(selected_examples)} examples with {word_length} words each")

        dataset = {
            'inputs': inputs,
            'targets': targets
        }

        return Dataset.from_dict(dataset)
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None

def load_logical_deduction_five_objects(filepath='https://raw.githubusercontent.com/suzgunmirac/BIG-Bench-Hard/main/bbh/tracking_shuffled_objects_five_objects.json', num_examples=10):
    try:
        response = requests.get(filepath)
        response.raise_for_status()
        data = json.loads(response.text)
        
        inputs = []
        targets = []

        # Iterate through examples and extract inputs and the correct answer
        for example in data['examples'][:num_examples]:
            inputs.append(example['input'])
            targets.append(example['target'])

        print(f"Loaded {len(inputs)} examples from the Five Objects dataset.")
        return Dataset.from_dict({'inputs': inputs, 'targets': targets})
    except Exception as e:
        print(f"Error loading Logical Deduction Five Objects dataset: {e}")
    return None

def load_logical_deduction_seven_objects(filepath='https://raw.githubusercontent.com/suzgunmirac/BIG-Bench-Hard/main/bbh/tracking_shuffled_objects_seven_objects.json', num_examples=100):
    try:
        response = requests.get(filepath)
        response.raise_for_status()
        data = json.loads(response.text)
        
        inputs = []
        targets = []

        # Iterate through examples and extract inputs and the correct answer
        for example in data['examples'][:num_examples]:
            inputs.append(example['input'])
            targets.append(example['target'])

        print(f"Loaded {len(inputs)} examples from the Seven Objects dataset.")
        return Dataset.from_dict({'inputs': inputs, 'targets': targets})
    except Exception as e:
        print(f"Error loading Logical Deduction Seven Objects dataset: {e}")
    return None