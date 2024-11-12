import json
import requests
import random
from datasets import Dataset

def load_word_sorting_dataset_by_length(word_length=8, num_examples=10):
    """
    Loads the Word Sorting dataset from local files.
    """
    try:
        if word_length == 8:
            filepath = '/Users/benwolley/prompt_game/data/word_sorting_8_words.json'
            max_examples = 10  # Fixed 10 examples for 8-word list
            # Always return exactly 10 examples for 8-word lists
            requested_examples = 10
        elif word_length == 10:
            filepath = '/Users/benwolley/prompt_game/data/word_sorting_10_words.json'
            max_examples = 100  # Allow selection of 10-100 examples for 10-word list
            # Use the requested number for 10-word lists
            requested_examples = num_examples
        else:
            raise ValueError("Invalid word length. Only 8 or 10 are supported.")
        
        print(f"\nDEBUG: Loading {word_length}-word dataset")
        print(f"DEBUG: Actually requesting {requested_examples} examples")
        
        # Load data from JSON file
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        total_examples = len(data['inputs'])
        print(f"DEBUG: Dataset contains {total_examples} total examples")
        
        if requested_examples > total_examples:
            print(f"DEBUG: Requested {requested_examples} examples but only {total_examples} available")
            raise ValueError(f"Requested {requested_examples} examples but only {total_examples} available")
            
        # Select random examples
        selected_indices = random.sample(range(total_examples), requested_examples)
        dataset = {
            'inputs': [data['inputs'][i] for i in selected_indices],
            'targets': [data['targets'][i] for i in selected_indices]
        }
        
        print(f"DEBUG: Successfully loaded {len(dataset['inputs'])} examples")
        return dataset

    except Exception as e:
        print(f"DEBUG: Error in load_word_sorting_dataset: {str(e)}")
        raise



def load_logical_deduction_five_objects():
    """
    Loads the Logical Deduction 5-object dataset from a local file.
    - Fixed at 10 examples for testing.
    """
    filepath = '/Users/benwolley/prompt_game/data/logical_deduction_5_objects.json'
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Dataset.from_dict(data)
    except Exception as e:
        print(f"Error loading Logical Deduction 5-object dataset: {e}")
        return None



def load_logical_deduction_three_objects(num_examples=10):
    """
    Loads the Logical Deduction 3-object dataset from a local file.
    Allows selection of 10-100 examples.
    """
    filepath = '/Users/benwolley/prompt_game/data/logical_deduction_3_objects.json'
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Clamp num_examples to be between 10 and 100
        num_examples = min(max(num_examples, 10), 100)
        selected_indices = random.sample(range(len(data['inputs'])), num_examples)
        selected_inputs = [data['inputs'][i] for i in selected_indices]
        selected_targets = [data['targets'][i] for i in selected_indices]
        
        dataset = {'inputs': selected_inputs, 'targets': selected_targets}
        print(f"Loaded {num_examples} examples from 3-object dataset from {filepath}")
        return Dataset.from_dict(dataset)
    except Exception as e:
        print(f"Error loading Logical Deduction 3-object dataset from {filepath}: {e}")
        return None

def load_causal_judgement(filepath='https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/causal_judgment/task.json', 
                          is_pretest=False, num_examples=100):
    """
    Loads the Causal Judgment dataset.
    - Pretest: Takes first 10 examples
    - Full test: Takes up to num_examples from remaining examples (after the first 10)
    
    Args:
        filepath: URL to the dataset
        is_pretest: Whether this is for pretest (loads pretest file) or full test (loads full test file)
        num_examples: Number of examples to load for full test
        
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
            # Take up to num_examples from remaining examples (11 onwards)
            remaining_examples = all_examples[10:]
            selected_examples = random.sample(remaining_examples, min(len(remaining_examples), num_examples))

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