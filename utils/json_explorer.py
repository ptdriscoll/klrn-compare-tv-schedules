import json

def load_json(input_path):
    """Loads a JSON file and returns the data."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def explore_json(obj, level=0, max_level=3, max_items=3):
    """
    Recursively explores a JSON object up to a specified depth.

    Args:
        obj (dict | list): JSON object to explore.
        level (int): Current depth level.
        max_level (int): Maximum depth to explore.
    """
    if level >= max_level or obj is None:
        return  

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (str, int, float, bool)):  # show simple values directly
                print('  ' * level + f'{key}: {value}')
            else:
                print('  ' * level + f'{key}: {type(value).__name__}')  # show type for complex values
            explore_json(value, level + 1, max_level, max_items)  # recurse deeper

    elif isinstance(obj, list):
        print('  ' * level + f'List[{len(obj)}] -> {type(obj[0]).__name__} (if not empty)')
        for i, item in enumerate(obj[:max_items]):  # show up to max_items
            print('  ' * (level + 1) + f'[{i}]')
            explore_json(item, level + 1, max_level, max_items)

def explore_json_file(filepath, max_level=3, max_items=3):
    """
    Loads and explores a JSON file up to a specified depth.

    Args:
        filepath (str): Path to the JSON file.
        max_level (int): Maximum depth to explore.
    """
    data = load_json(filepath)
    if data is not None:
        print(f"Exploring JSON file: {filepath}\n")
        explore_json(data, max_level=max_level, max_items=max_items)
