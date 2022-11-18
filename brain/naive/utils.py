from pathlib import Path
from typing import Dict
import json


def load_credentials(secret_file: Path = "neo4j.json") -> Dict:
    """Load credentials from a json secret file

    :param secret_file: file path with secret, defaults to "neo4j.json"
    :type secret_file: Path, optional
    :return: dictionary contains the json key pair
    :rtype: Dict
    """
    with secret_file.open() as json_file:
        data = json.load(json_file)
        
    return data