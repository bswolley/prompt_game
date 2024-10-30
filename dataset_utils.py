import json
import requests
from datasets import Dataset

def download_word_sorting_dataset_by_length(word_length=8):
    """Download BIG-bench word sorting dataset for fixed 8-word examples."""
    url = "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/word_sorting/task.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)
        
        # Filter for specified word length examples and select fixed examples by index
        examples = data['examples']
        filtered_examples = [ex for ex in examples if len(ex['input'].split()) == word_length]
        
        if not filtered_examples:
            raise ValueError(f"No {word_length}-word examples found in the dataset")
        
        # Use a fixed slice for consistency
        selected_examples = filtered_examples[:10]
        
        inputs = [example['input'] for example in selected_examples]
        targets = [example['target'] for example in selected_examples]
        
        dataset = {
            'inputs': inputs,
            'targets': targets
        }
        
        return Dataset.from_dict(dataset)
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None