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
        print(f"Debug - Initialized DatasetManager:")
        print(f"Debug - Base dir: {self.base_dir}")
        print(f"Debug - Data dir: {self.data_dir}")
        print(f"Debug - Config path: {self.config_path}")

    def load_config(self):
        """Load dataset configurations."""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
                print(f"Debug - Loaded config successfully")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.config = {}

    def load_dataset(self, dataset_type: str, mode: str = "practice", num_examples: Optional[int] = None):
        """
        Generic dataset loader that works with any dataset following the config structure.
        """
        try:
            print(f"\nDebug - Loading dataset: {dataset_type}, mode: {mode}")
            
            # Get dataset config
            if dataset_type not in self.config:
                print(f"Debug - Dataset {dataset_type} not found in config")
                raise ValueError(f"Dataset {dataset_type} not found in config")
            
            if mode not in self.config[dataset_type]:
                print(f"Debug - Mode {mode} not found for dataset {dataset_type}")
                raise ValueError(f"Mode {mode} not found for dataset {dataset_type}")
            
            dataset_config = self.config[dataset_type][mode]
            print(f"Debug - Dataset config: {dataset_config}")
            
            # Load data file
            if "file_path" not in dataset_config:
                print(f"Debug - No file_path in config for {dataset_type} {mode}")
                raise ValueError(f"No file_path specified for {dataset_type} {mode}")
                
            file_path = self.data_dir / dataset_config["file_path"]
            print(f"Debug - Attempting to load file: {file_path}")
            print(f"Debug - File exists: {file_path.exists()}")
            
            if not file_path.exists():
                raise FileNotFoundError(f"Dataset file not found: {file_path}")
                
            with open(file_path) as f:
                raw_data = json.load(f)
                print(f"Debug - Successfully loaded raw data")

            # Handle different dataset types
            if dataset_type == "translation_task":
                return {
                    'examples': raw_data['examples'],
                    'dataset_type': 'translation_task',
                    'dataset_info': self.config[dataset_type]
                }
            elif dataset_type == "complex_transformation":
                examples = raw_data.get('examples', [])
                if not examples:
                    print("Debug - No examples found in complex transformation dataset")
                    raise ValueError("No examples found in complex transformation dataset")

                print(f"Debug - Found {len(examples)} examples in dataset")
                
                if mode == "practice":
                    selected_examples = examples
                else:  # test mode
                    selected_examples = [random.choice(examples)]
                    print(f"Debug - Selected 1 random example for test mode")

                return {
                    'examples': selected_examples,
                    'dataset_type': 'complex_transformation',
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
                    print("Debug - Invalid dataset format")
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
                    print(f"Debug - Requested {num_examples} examples but only {total_examples} available")
                    raise ValueError(f"Requested {num_examples} examples but only {total_examples} available")

                # Select examples
                indices = random.sample(range(total_examples), num_examples)
                print(f"Debug - Selected {num_examples} examples from {total_examples} total")

                return {
                    'inputs': [data['inputs'][i] for i in indices],
                    'targets': [data['targets'][i] for i in indices],
                    'dataset_type': dataset_type,
                    'dataset_info': self.config[dataset_type]
                }

        except Exception as e:
            print(f"Error loading dataset {dataset_type}: {str(e)}")
            raise