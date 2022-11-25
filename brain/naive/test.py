from brain.naive.neo4j_db import Neo4j
import logging
from brain.naive import utils


def test():
    """This is used to display relationships between nodes. 
    """
    app = Neo4j()
    while True:
        response = input("Use this format to find all relationships "
                         "('exit' to quit): \n"
                         "<node1 name> <node1 type> :\n")
        if response == "exit":
            break

        node_name, node_type, = response.split(" ")

        edges = app.find_all_edge(node_type=node_type,
                                  node_name=node_name)
        utils.display_edge(edges=edges)


def main():
    test()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
