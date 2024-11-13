from pathlib import Path
import json
from typing import Dict, List, Optional
import random

class DatasetManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.config_path = self.base_dir / 'config' / 'datasets.json'
        self.load_config()

    def load_config(self):
        """Load dataset configurations."""
        with open(self.config_path) as f:
            self.config = json.load(f)

    def load_dataset(self, dataset_type: str, mode: str = "practice", num_examples: Optional[int] = None):
        """
        Generic dataset loader that works with any dataset following the config structure.
        
        The config (datasets.json) for each dataset should specify:
        - file_path: where to find the data
        - input_field: what field in the JSON contains the input (e.g., "document", "inputs")
        - target_field: what field contains the target (e.g., "summary", "targets")
        - num_examples or min/max_examples: how many examples to use
        """
        try:
            # Get dataset config
            if dataset_type not in self.config:
                raise ValueError(f"Dataset {dataset_type} not found in config")
            
            dataset_config = self.config[dataset_type][mode]
            
            # Load data file
            file_path = self.data_dir / dataset_config["file_path"]
            with open(file_path) as f:
                raw_data = json.load(f)

            # Handle different data structures
            input_field = dataset_config.get("input_field", "inputs")
            target_field = dataset_config.get("target_field", "targets")
            
            # Convert data to standard format if needed
            if isinstance(raw_data, list):
                # Data is a list of examples
                data = {
                    'inputs': [item[input_field] for item in raw_data],
                    'targets': [item[target_field] for item in raw_data]
                }
            else:
                # Data already has inputs/targets lists
                data = raw_data

            # Handle number of examples
            total_examples = len(data['inputs'])
            if dataset_config.get("fixed_size", False):
                num_examples = dataset_config["num_examples"]
            else:
                min_examples = dataset_config.get("min_examples", 10)
                max_examples = dataset_config.get("max_examples", total_examples)
                num_examples = min(max(num_examples or min_examples, min_examples), max_examples)

            if num_examples > total_examples:
                raise ValueError(f"Requested {num_examples} examples but only {total_examples} available")

            # Select examples
            selection_method = dataset_config.get("selection", "random")
            if selection_method == "random":
                indices = random.sample(range(total_examples), num_examples)
            elif selection_method == "first":
                indices = list(range(num_examples))
            else:
                raise ValueError(f"Unknown selection method: {selection_method}")

            return {
                'inputs': [data['inputs'][i] for i in indices],
                'targets': [data['targets'][i] for i in indices],
                'dataset_info': self.config[dataset_type]
            }

        except Exception as e:
            print(f"Error loading dataset {dataset_type}: {str(e)}")
            raise