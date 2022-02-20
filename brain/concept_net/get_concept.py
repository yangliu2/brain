""" User ConceptNet to find relations between concepts. """
import requests
from typing import List, Dict
from pprint import pprint


def get_concepts(concept_name: str,
                 lang: str = "en") -> Dict:
    """ Get the concept from ConceptNet. """
    url = f'https://api.conceptnet.io/c/{lang}/{concept_name}'
    response = requests.get(url)
    obj = response.json()
    return obj


def get_related_concepts(concept_name: str,
                         query_lang: str = "en",
                         related_lang: str = "en") -> Dict:
    """ Find all the related concepts. """
    url = f'https://api.conceptnet.io/related/c/{query_lang}/{concept_name}' \
          f'?filter=/c/{related_lang}'
    
    response = requests.get(url)
    obj = response.json()
    return obj


def find_relations(concept_1: str,
                   concept_2: str,
                   query_lang: str = "en") -> List:
    """ Find relations between two concepts. """
    url = f'http://api.conceptnet.io//query?node=/c/{query_lang}/' \
          f'{concept_1}&other=/c/{query_lang}/{concept_2}'
    response = requests.get(url)
    obj = response.json()
    relations = [edge['surfaceText']
                 for edge in obj['edges'] if 'surfaceText' in edge]
    return relations
