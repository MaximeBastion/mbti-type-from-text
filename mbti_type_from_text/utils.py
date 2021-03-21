import json
import os
from pathlib import Path


def get_object_from_string(string):
    components = string.split(".")
    object_name = components[-1]
    module_path = ".".join(components[:-1])
    module = __import__(module_path, fromlist=[object_name])
    return getattr(module, object_name)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(obj, path):
    parent_folder = Path(path).parent.absolute()
    Path(parent_folder).mkdir(parents=True, exist_ok=True)  # create parent directory if it doesn't exist
    with open(path, "w") as f:
        json.dump(obj, f)
