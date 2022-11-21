from rich.table import Table
from rich.console import Console
import argparse
from typing import List
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


def display_table(rows: List[List[str]]):
    """Use Rich package to generate a CLI output

    :param rows: 2d list rows as input
    :type rows: List
    """

    table = Table()
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Target", justify="left", style="magenta")
    table.add_column("Relationship", justify="left", style="green")

    # add each row to the table
    [table.add_row(*x) for x in rows]

    console = Console()
    console.print(table)


def display_relationship(relations: List[Dict]):
    """Use Rich package for display

    :param relations: relationship as a list of dict
    :type relations: List[Dict]
    """
    # Made a 2d list so it fits into the table structure
    node_2d_list = [[str(x)
                    for row in relations
                    for x in row.values()]]

    display_table(rows=node_2d_list)
