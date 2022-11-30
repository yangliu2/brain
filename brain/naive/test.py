from brain.naive.neo4j_db import Neo4j
from loguru import logger
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

        response_fields = response.split(" ")
        if len(response_fields) == 2:
            node_name, node_type = response_fields
            edges = app.find_all_edge(node_type=node_type,
                                      node_name=node_name)
        elif len(response_fields) == 1:
            (node_name,) = response_fields
            node_type = None
            edges = app.find_all_edge(node_type=node_type,
                                      node_name=node_name)
        utils.display_edge(edges=edges)


def main():
    test()


if __name__ == "__main__":
    logger.add("testing.log")
    main()
