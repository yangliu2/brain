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

        relationships = app.find_all_relationships(relationship="KNOWS",
                                                  node_type="Person",
                                                  node_name="Yang")
        utils.display_relationship(relations=relationships)


def main():
    test()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
