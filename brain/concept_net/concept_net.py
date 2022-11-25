""" User ConceptNet to find relations between concepts. """
import requests
from typing import List, Dict
from pprint import pprint
from dataclasses import dataclass
from enum import Enum


class RelationTypesEnum(Enum):
    """These are the relationships we are interested in getting from Concept Net

    :param Enum: Make it a Enum class
    :type Enum: Enum
    """
    PART_OF = "PartOf"
    AT_LOCATION = "AtLocation"
    CAPABLE_OF = "CapableOf"
    USED_FOR = "UsedFor"
    

class Neo4jTypesEnum(Enum):
    """These are enums for converting ConceptNet relationships to Neo4j ones

    :param Enum: Make it a Enum class
    :type Enum: Enum
    """
    PART_OF = "PART_OF"
    AT_LOCATION = "AT_LOCATION"
    CAPABLE_OF = "CAPABLE_OF"
    USED_FOR = "USED_FOR"


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
        """Get the concept from ConceptNet. This will return all the concepts
        that's directly related to the current concept.

        :return: the payload regarding the concept
        :rtype: Dict
        """
        url = f'https://api.conceptnet.io/c/{self.lang}/{self.concept_name}'
        response = requests.get(url)
        obj = response.json()
        return obj

    def format_for_neo4j(self,
                         conceptnet_output: Dict) -> Dict:
        """Format the Concept Net output according to the relationship we 
        liked. This is selected in the Enums, but can be a config in the 
        future. Start and end node used the @id url instead of the 'label'
        because it's all in one word, so it's easier to neo4j storage. 

        :param conceptnet_output: the dict output from Concept Net 
        :type conceptnet_output: Dict
        :return: The formated output after filter and selection. 
        :rtype: Dict
        """
        interested_list = [x.value for x in RelationTypesEnum]
        relations = [{'n1': edge['start']['@id'].split('/')[-1],
                     'r': self.convert_relations(edge['rel']['label']),
                     'n2': edge['end']['@id'].split('/')[-1]}
                     for edge in conceptnet_output['edges']
                     if edge['rel']['label'] in interested_list]
        return relations

    @staticmethod
    def convert_relations(relation: str) -> str:
        """Convert Concetp Net relationship names to Neo4j relationship names

        :param relation: relationship name in Concept Net format
        :type relation: str
        :return: relationship name in Neo4j format
        :rtype: str
        """

        name_map = {x.value: Neo4jTypesEnum(x.name).value 
                    for x in RelationTypesEnum}
        return name_map[relation]

    def get_related_concepts(self) -> Dict:
        """Find all the related concepts. These concepts may not be directly
        related. 

        :return: json for all the concepts related to the current concept
        :rtype: Dict
        """
        url = f"https://api.conceptnet.io/related/c/{self.lang}/" \
              f'{self.concept_name}?filter=/c/{self.lang}'

        response = requests.get(url)
        obj = response.json()
        return obj

    def find_relations(self,
                       target_concept: str) -> List[str]:
        """Find relations between two concepts.

        :param target_concept: the target concept like to connect the current 
        concept to
        :type target_concept: str
        :return: list of relationship between the two concepts
        :rtype: List[str]
        """
        url = f'http://api.conceptnet.io//query?node=/c/{self.lang}/' \
              f'{self.concept_name}&other=/c/{self.lang}/{target_concept}'
        response = requests.get(url)
        obj = response.json()
        relations = [edge['surfaceText']
                     for edge in obj['edges'] if 'surfaceText' in edge]
        return relations


def main():
    concept = ConceptNet(concept_name="leaf")
    related = concept.get_concepts()
    relations = concept.format_for_neo4j(conceptnet_output=related)
    pprint(relations)


if __name__ == "__main__":
    main()
