"""Utility functions for model management"""

import os
from pathlib import Path
from typing import List


def read_models_from_file() -> List[str]:
    """Read supported models from models.txt file"""
    models_file = Path(__file__).parent.parent.parent / "models.txt"

    if not models_file.exists():
        # Return default models if file doesn't exist
        return ["moondream:1.8b", "llava:latest", "llama3.2-vision:latest"]

    models = []
    with open(models_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                models.append(line)

    return models


def get_default_model() -> str:
    """Get the default model (first model in the list)"""
    models = read_models_from_file()
    return models[0] if models else "moondream:1.8b"


def is_supported_model(model_name: str) -> bool:
    """Check if a model is in the supported models list"""
    supported_models = read_models_from_file()
    return model_name in supported_models