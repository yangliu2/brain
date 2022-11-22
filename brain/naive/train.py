from brain.naive.neo4j_db import Neo4j
import logging

def train():
    """This is used to modify relationships between nodes. 
    """
    app = Neo4j()
    while True:
        response = input("Please indicate relationship in the format "
                         "('exit' to quit): \n"
                         "<node1 name> <node1 type> <relationship> "
                         "<node2> <node2 type>:\n")
        if response == "exit":
            break

        node1_name, node1_type, relationship, node2_name, node2_type = \
            response.split(" ")

        app.create_relationship(relationship=relationship,
                                node1_type=node1_type,
                                node2_type=node2_type,
                                node1_name=node1_name,
                                node2_name=node2_name)


def main():
    train()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
