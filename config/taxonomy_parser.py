from typing import Dict, Set

def parse_taxonomy(file_path: str) -> Dict[str, Dict[str, Set[str]]]:
    """
    Parses a taxonomy file and returns a structured dictionary.

    Args:
        file_path (str): The path to the taxonomy file.

    Returns:
        Dict[str, Dict[str, Set[str]]]: A dictionary representing the taxonomy.
    """
    taxonomy: Dict[str, Dict[str, Set[str]]] = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if '|' in line:
                parts = line.split(':')
                category_subcategory = parts[0].split('|')
                category = category_subcategory[0].strip()
                subcategory = category_subcategory[1].strip()
                keywords = {kw.strip() for kw in parts[1].split(',')}
                
                if category not in taxonomy:
                    taxonomy[category] = {}
                taxonomy[category][subcategory] = keywords
            else:
                parts = line.split(':')
                category = parts[0].strip()
                if category not in taxonomy:
                    taxonomy[category] = {}
    return taxonomy
