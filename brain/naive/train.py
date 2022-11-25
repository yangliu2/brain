from brain.naive.neo4j_db import Neo4j
from brain.concept_net.concept_net import ConceptNet
from typing import List, Dict
import logging


def add_concept_net_edges(nodes: List[str]):
    """Add relationshps got from concept net

    :param nodes: the nodes used for searching for edges in concept net
    :type nodes: List[str]
    """

    # get all relationship for both nodes from concept net
    concept_net_edges = []
    for node in nodes:
        concept = ConceptNet(concept_name=node)
        related = concept.get_concepts()
        nodes = concept.format_for_neo4j(conceptnet_output=related)
        concept_net_edges.extend(nodes)

    # ask which relationship to add
    edges_display = "\n".join([f"({i}): {x['n1']} {x['r']} {x['n2']}"
                               for i, x in enumerate(concept_net_edges)])

    include = input(f"Would you like to include any of these concepts? "
                    f"All (y), Select(s), Manual Input(m)\n"
                    f"{edges_display}\n>:")

    # add relationships according to user choices
    if include in ['all', 'All', 'yes', 'y', 'YES']:
        # add all relationships
        add_edges(edges=concept_net_edges)
    elif include in ['select', 'Select', 's', 'S']:
        choices = input("Please enter the relationship you would like to add")
        int_choices = [int(x) for x in choices]
        chosen_edges = [concept_net_edges[x] for x in int_choices]
        add_edges(edges=chosen_edges)
    elif include in ['Manual', 'manual', 'm', 'M']:
        response = input("Please indicate relationship in the format "
                         "<node1 name> <node1 type> <relationship> "
                         "<node2> <node2 type>:\n")
        node1_name, node1_type, edge, node2_name, node2_type = \
            response.split(" ")

        app.create_edge(edge=edge,
                        node1_type=node1_type,
                        node2_type=node2_type,
                        node1_name=node1_name,
                        node2_name=node2_name)


def add_edges(edges: Dict,
              node_type: str = "unknown"):
    """Add relationship in neo4j using the given data. Each edge is a dict
    with n1, n2 as nodes, and r as the relationship

    :param edges: edges got from concept net
    :type edges: str
    :param node_type: the default edge type because neo4j requires a label for
    the node, defaults to "unknown"
    :type node_type: str, optional
    """
    for edge in edges:
        node1_name = edge["n1"]
        node2_name = edge['n2']
        edge = edge['r']

        app.create_edge(edge=edge,
                        node1_type=node_type,
                        node2_type=node_type,
                        node1_name=node1_name,
                        node2_name=node2_name)


def train():
    """This is used to modify relationships between nodes. 
    """

    while True:
        response = input("Please indicate relationship in the format "
                         "('exit' to quit): \n"
                         "<node1 name> <node1 type> <relationship> "
                         "<node2> <node2 type>:\n")
        if response == "exit":
            break

        node1_name, node1_type, edge, node2_name, node2_type = \
            response.split(" ")

        app.create_edge(edge=edge,
                        node1_type=node1_type,
                        node2_type=node2_type,
                        node1_name=node1_name,
                        node2_name=node2_name)

        # add concept net edges
        add_concept_net_edges(nodes=[node1_name, node2_name])


def main():
    train()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    app = Neo4j()
    main()
