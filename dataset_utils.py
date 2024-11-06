import json
import requests
import random
from datasets import Dataset

def download_word_sorting_dataset_by_length(word_length=8):
    url = "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/word_sorting/task.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)

        examples = data['examples']
        filtered_examples = [ex for ex in examples if len(ex['input'].split()) == word_length]

        if not filtered_examples:
            raise ValueError(f"No {word_length}-word examples found in the dataset")

        max_examples = 10 if word_length == 8 else 100
        selected_examples = random.sample(filtered_examples, min(len(filtered_examples), max_examples))

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
        
        # Randomly sample unique examples
        selected_examples = random.sample(data['examples'], min(len(data['examples']), num_examples))

        inputs = [example['input'] for example in selected_examples]
        targets = [example['target'] for example in selected_examples]

        print(f"Loaded {len(inputs)} unique examples from the Five Objects dataset.")
        return Dataset.from_dict({'inputs': inputs, 'targets': targets})
    except Exception as e:
        print(f"Error loading Logical Deduction Five Objects dataset: {e}")
    return None

def load_logical_deduction_three_objects(filepath='https://raw.githubusercontent.com/suzgunmirac/BIG-Bench-Hard/main/bbh/tracking_shuffled_objects_three_objects.json', num_examples=100):
    try:
        response = requests.get(filepath)
        response.raise_for_status()
        data = json.loads(response.text)
        
        # Randomly sample unique examples
        selected_examples = random.sample(data['examples'], min(len(data['examples']), num_examples))

        inputs = [example['input'] for example in selected_examples]
        targets = [example['target'] for example in selected_examples]

        print(f"Loaded {len(inputs)} unique examples from the Three Objects dataset.")
        return Dataset.from_dict({'inputs': inputs, 'targets': targets})
    except Exception as e:
        print(f"Error loading Logical Deduction Three Objects dataset: {e}")
    return None

def load_causal_judgement(filepath='https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/causal_judgment/task.json', is_pretest=False, num_examples=100):
    """
    Loads the causal judgment dataset.
    For pretest: Always takes first 10 examples
    For full test: Takes specified number (10-100) from remaining examples
    
    Args:
        filepath: URL to the dataset
        is_pretest: Whether this is for pretest (first 10) or full test (random from rest)
        num_examples: Number of examples to load for full test (ignored for pretest)
        
    Returns:
        Dataset: Contains 'inputs' and 'targets' where targets are 'Yes' or 'No'
    """
    try:
        response = requests.get(filepath)
        response.raise_for_status()
        data = json.loads(response.text)
        
        all_examples = data['examples']
        
        if is_pretest:
            # Take first 10 examples for pretest
            selected_examples = all_examples[:10]
        else:
            # Take random sample from remaining examples (11 onwards)
            remaining_examples = all_examples[10:]
            num_examples = min(max(10, num_examples), 100)  # Ensure between 10 and 100
            selected_examples = random.sample(remaining_examples, num_examples)

        inputs = []
        targets = []
        
        for example in selected_examples:
            inputs.append(example['input'])
            # Convert target_scores to Yes/No
            target = "Yes" if example['target_scores']['Yes'] == 1 else "No"
            targets.append(target)

        print(f"Loaded {len(inputs)} examples from the Causal Judgement dataset {'(pretest)' if is_pretest else '(full test)'}")
        return Dataset.from_dict({'inputs': inputs, 'targets': targets})
    except Exception as e:
        print(f"Error loading Causal Judgement dataset: {e}")
        return None