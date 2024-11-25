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
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.config = {}

    def load_dataset(self, dataset_type: str, mode: str = "practice", num_examples: Optional[int] = None):
        """
        Generic dataset loader that works with any dataset following the config structure.
        """
        try:
            # Get dataset config
            if dataset_type not in self.config:
                raise ValueError(f"Dataset {dataset_type} not found in config")
            
            if mode not in self.config[dataset_type]:
                raise ValueError(f"Mode {mode} not found for dataset {dataset_type}")
            
            dataset_config = self.config[dataset_type][mode]
            
            # Load data file
            file_path = self.data_dir / dataset_config["file_path"]
            if not file_path.exists():
                raise FileNotFoundError(f"Dataset file not found: {file_path}")
                
            with open(file_path) as f:
                raw_data = json.load(f)

            # Handle different dataset types
            if dataset_type == "translation_task":
                # For translation task, keep the original format
                return {
                    'examples': raw_data['examples'],
                    'dataset_type': 'translation_task',
                    'dataset_info': self.config[dataset_type]
                }
            else:
                # Handle other dataset types (word sorting, logical deduction, etc.)
                input_field = dataset_config.get("input_field", "inputs")
                target_field = dataset_config.get("target_field", "targets")
                
                # Convert data to standard format
                if isinstance(raw_data, list):
                    # Data is a list of examples
                    data = {
                        'inputs': [item[input_field] for item in raw_data],
                        'targets': [item[target_field] for item in raw_data]
                    }
                else:
                    # Data already has inputs/targets lists
                    data = raw_data

                # Validate data structure
                if not isinstance(data, dict) or 'inputs' not in data or 'targets' not in data:
                    raise ValueError("Invalid dataset format")

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
                indices = random.sample(range(total_examples), num_examples)

                return {
                    'inputs': [data['inputs'][i] for i in indices],
                    'targets': [data['targets'][i] for i in indices],
                    'dataset_type': dataset_type,
                    'dataset_info': self.config[dataset_type]
                }

        except Exception as e:
            print(f"Error loading dataset {dataset_type}: {str(e)}")
            raise