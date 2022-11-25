""" User ConceptNet to find relations between concepts. """
import requests
from typing import List, Dict
from pprint import pprint
from dataclasses import dataclass


@dataclass
class ConceptNet():
    """This is the object that use concept net to get related nodes
    and relationships. https://conceptnet.io/

    :param concept_name: the name of the concept for getting all of the concepts
    :type concept_name: str
    :param lang: language of the concept 
    :type lang: str
    """
    concept_name: str
    lang: str = 'en'

    def get_concepts(self) -> Dict:
        """ Get the concept from ConceptNet. """
        url = f'https://api.conceptnet.io/c/{self.lang}/{self.concept_name}'
        response = requests.get(url)
        obj = response.json()
        return obj

    def get_related_concepts(self) -> Dict:
        """ Find all the related concepts. """
        url = f"https://api.conceptnet.io/related/c/{self.lang}/" \
              f'{self.concept_name}?filter=/c/{self.lang}'

        response = requests.get(url)
        obj = response.json()
        return obj

    def find_relations(self,
                       target_concept: str) -> List:
        """ Find relations between two concepts. """
        url = f'http://api.conceptnet.io//query?node=/c/{self.query_lang}/' \
            f'{self.concept_name}&other=/c/{self.query_lang}/{target_concept}'
        response = requests.get(url)
        obj = response.json()
        relations = [edge['surfaceText']
                     for edge in obj['edges'] if 'surfaceText' in edge]
        return relations


def main():
    concept = ConceptNet(concept_name="leaf")
    related = concept.get_concepts()
    pprint(related)


if __name__ == "__main__":
    main()
