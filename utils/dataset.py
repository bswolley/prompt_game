import json
import requests
from datasets import Dataset
from utils.logger import Logger

logger = Logger().get_logger()

def download_word_sorting_dataset_by_length(word_length=8):
    """Download BIG-bench word sorting dataset for fixed 8-word examples."""
    url = "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/word_sorting/task.json"
    try:
        logger.info(f"Downloading word sorting dataset for {word_length}-word examples")
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)
        
        # Filter for specified word length examples and select fixed examples by index
        examples = data['examples']
        filtered_examples = [ex for ex in examples if len(ex['input'].split()) == word_length]
        
        if not filtered_examples:
            logger.error(f"No {word_length}-word examples found in the dataset")
            raise ValueError(f"No {word_length}-word examples found in the dataset")
        
        logger.debug(f"Found {len(filtered_examples)} examples with {word_length} words")
        
        # Use a fixed slice for consistency
        selected_examples = filtered_examples[:10]
        logger.info(f"Selected {len(selected_examples)} examples for testing")
        
        inputs = [example['input'] for example in selected_examples]
        targets = [example['target'] for example in selected_examples]
        
        dataset = {
            'inputs': inputs,
            'targets': targets
        }
        
        logger.debug("Successfully created dataset from examples")
        return Dataset.from_dict(dataset)
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while downloading dataset: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while processing dataset: {e}", exc_info=True)
        return None