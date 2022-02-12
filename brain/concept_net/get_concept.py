import requests
from typing import List, Dict

def get_concepts(concept_name: str) -> Dict:
    url = f'https://api.conceptnet.io/c/en/{concept_name}'
    response = requests.get(url)
    obj = response.json()
    return obj

def get_related_concepts(concept_name: str) -> List[Dict]:
    url = f'https://api.conceptnet.io/related/c/en/{concept_name}?filter=/c/en'
    response = requests.get(url)
    obj = response.json()
    return obj