from neo4j import GraphDatabase
import logging
from pathlib import Path
from typing import List, Dict
from brain.naive import utils
from neo4j.exceptions import ServiceUnavailable
from enum import Enum


class Neo4jEnums(Enum):
    URI = "uri"
    USER = "user"
    PASSWORD = "password"
    NEO4J = "neo4j"


class Neo4j:
    """This object will be used to manipulate Neo4j graphical database.
    """

    def __init__(self):
        # Load credential from secret file
        credentials = utils.load_credentials(
            secret_file=Path("brain/naive/neo4j.json"))

        # Connet to the neo4j driver
        self.driver = GraphDatabase.driver(
            uri=credentials[Neo4jEnums.URI.value],
            auth=(credentials[Neo4jEnums.USER.value],
                  credentials[Neo4jEnums.PASSWORD.value]))

    def close(self):
        """Close the connections
        """
        self.driver.close()

    def create_node(self,
                    node_type: str,
                    node_name: str) -> None:
        """Create a node in the database

        :param node_type: type of node
        :type node_type: str
        :param node_name: name of the node
        :type node_name: str
        """
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            # Write transactions allow the driver to handle retries and
            #  transient errors
            result = session.execute_write(
                self._create_node,
                node_type,
                node_name)
            for row in result:
                logging.info(f"Created node {row['n']}")

    @staticmethod
    def _create_node(tx,
                     node_type: str,
                     node_name: str) -> List[Dict]:
        """Transaction function to create the node

        :param tx: transcation function
        :type tx: unknow, Callable
        :param node_type: node type
        :type node_type: str
        :param node_name: node name
        :type node_name: str
        :return: List of Dict
        :rtype: List[Dict]
        """

        query = (
            f"CREATE (n:{node_type} {{ name: $node_name }}) "
            f"RETURN n"
        )
        result = tx.run(query,
                        node_name=node_name)
        try:
            return [{"n": row["n"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise

    def create_relationship(self,
                            relationship: str,
                            node1_type: str,
                            node2_type: str,
                            node1_name: str,
                            node2_name: str):
        """Create a relationship with two nodes. The relationship is 
        unidirectional

        :param relationship: indicate the relaitonship between two nodes. This
        string is normally all caps to indicate it's a relationship
        :type relationship: str
        :param node1_type: indicate the type of node 1
        :type node1_type: str
        :param node1_type: indicate the type of node 2
        :type node1_type: str
        :param node1_name: name of node one
        :type node1_name: str
        :param node2_name: name of node two
        :type node2_name: str
        """
        # Create nodes if they don't exist
        if not self.find_node(node_type=node1_type,
                              node_name=node1_name):
            self.create_node(node_type=node1_type,
                             node_name=node1_name)
        if not self.find_node(node_type=node2_type,
                              node_name=node2_name):
            self.create_node(node_type=node2_type,
                             node_name=node2_name)

        # create relationship if it doesn't already exist
        if not self.find_relationship(relationship=relationship,
                                      node1_type=node1_type,
                                      node2_type=node2_type,
                                      node1_name=node1_name,
                                      node2_name=node2_name):
            with self.driver.session(
                    database=Neo4jEnums.NEO4J.value) as session:
                # Write transactions allow the driver to handle retries and
                #  transient errors
                result = session.execute_write(
                    self._create_and_return_relationship,
                    relationship,
                    node1_type,
                    node2_type,
                    node1_name,
                    node2_name)
                for row in result:
                    logging.info(f"Created {relationship} between: "
                                 f"{row['n1']}, {row['n2']}")
        else:
            logging.info(f"Relationship {relationship} already existed between "
                         f"{node1_name} and {node2_name}")

    @staticmethod
    def _create_and_return_relationship(tx,
                                        relationship: str,
                                        node1_type: str,
                                        node2_type: str,
                                        node1_name: str,
                                        node2_name: str,
                                        confidence: float = 0.5) -> List[Dict]:
        """Actually create the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param relationship: how node1 is related to node 2, all caps to 
        indicate relationship
        :type relationship: str
        :param node1_type: type for node 1, cap first letter
        :type node1_type: str
        :param node2_type: type of node 2, cap the first letter
        :type node2_type: str
        :param node1_name: name for node 1
        :type node1_name: str
        :param node2_name: name for node 2
        :type node2_name: str
        :param confidence: confidence of the relationship, default to 0.5
        :type confidence: float
        :return: List of dict 
        :rtype: List of Dict
        """
        # To learn more about the Cypher syntax,
        #  see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords
        #  https://neo4j.com/docs/cypher-refcard/current/

        query = (
            f"MATCH (n1: {node1_type}), (n2: {node2_type}) "
            f"WHERE n1.name = '{node1_name}' AND n2.name = '{node2_name}' "
            f"CREATE (n1)-[r: {relationship} "
            f"{{ confidence: {confidence} }}]->(n2) "
            f"RETURN n1, n2"
        )

        result = tx.run(query)
        try:
            return [{"n1": row["n1"]["name"], "n2": row["n2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise

    def find_relationship(self,
                          relationship: str,
                          node1_type: str,
                          node2_type: str,
                          node1_name: str,
                          node2_name: str) -> List[Dict[str, str]]:
        """Find a relationship with two nodes. The relationship is 
        unidirectional.

        :param relationship: indicate the relaitonship between two nodes. This
        string is normally all caps to indicate it's a relationship
        :type relationship: str
        :param node1_type: indicate the type of node 1
        :type node1_type: str
        :param node1_type: indicate the type of node 2
        :type node1_type: str
        :param node1_name: name of node one
        :type node1_name: str
        :param node2_name: name of node two
        :type node2_name: str
        :return: List of Dict
        :rtype: List[Dict[str,str]]
        """
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            # Write transactions allow the driver to handle retries and
            #  transient errors
            result = session.execute_write(
                self._find_relationship,
                relationship,
                node1_type,
                node2_type,
                node1_name,
                node2_name)
            for row in result:
                logging.info(f"Found relationship({relationship}) between: "
                             f"{row['n1']}, {row['n2']}")

            # return relationships if found any
            return [row for row in result]

    @staticmethod
    def _find_relationship(tx,
                           relationship: str,
                           node1_type: str,
                           node2_type: str,
                           node1_name: str,
                           node2_name: str) -> List[Dict]:
        """Actually find the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param relationship: how node1 is related to node 2, all caps to 
        indicate relationship
        :type relationship: str
        :param node1_type: type for node 1, cap first letter
        :type node1_type: str
        :param node2_type: type of node 2, cap the first letter
        :type node2_type: str
        :param node1_name: name for node 1
        :type node1_name: str
        :param node2_name: name for node 2
        :type node2_name: str
        :return: List of dict 
        :rtype: List of Dict
        """
        # To learn more about the Cypher syntax,
        #  see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords
        #  https://neo4j.com/docs/cypher-refcard/current/

        query = (
            f"MATCH (n1: {node1_type})-[r:{relationship}]->(n2:{node2_type}) "
            f"WHERE n1.name = '{node1_name}' AND n2.name = '{node2_name}' "
            f"RETURN n1, n2, r"
        )
        result = tx.run(query)
        try:
            return [{"n1": row["n1"]["name"],
                     "n2": row["n2"]["name"],
                     "r": relationship}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise

    def find_all_relationships(self,
                               node_type: str,
                               node_name: str) -> List[Dict[str, str]]:
        """Find all relationships with originated from the starting node. The 
        relationship is unidirectional.

        :param node_type: indicate the type of node 1
        :type node_type: str
        :param node_name: name of node one
        :type node_name: str
        :return: List of Dict
        :rtype: List[Dict[str,str]]
        """
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            # Write transactions allow the driver to handle retries and
            #  transient errors
            result = session.execute_write(
                self._find_all_relationships,
                node_type,
                node_name)
            for row in result:
                logging.info(f"Found relationship({row['r']}) between: "
                             f"{row['n1']}, {row['n2']}")

            # return relationships if found any
            return [row for row in result]

    @staticmethod
    def _find_all_relationships(tx,
                                node1_type: str,
                                node1_name: str) -> List[Dict]:
        """Actually find the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param node_type: type for node, cap first letter
        :type node_type: str
        :param node_name: name for node
        :type node_name: str
        :return: List of dict 
        :rtype: List of Dict
        """
        # get all relationships originated to the node
        query = (
            f"MATCH(n1: {node1_type} {{name: '{node1_name}'}})-[r]->(n2) "
            f"RETURN n1, r, n2"
        )
        result1 = tx.run(query)

        # get all relationships directed towards the node
        query = (
            f"MATCH(n1)-[r]->(n2:{node1_type} {{name: '{node1_name}'}}) "
            f"RETURN n1, r, n2"
        )
        result2 = tx.run(query)

        try:
            result1_list = [{"n1": row["n1"]["name"],
                             "r": str(row['r'].type),
                             "n2": row["n2"]["name"]}
                            for row in result1]
            result2_list = [{"n1": row["n1"]["name"],
                             "r": str(row['r'].type),
                             "n2": row["n2"]["name"]}
                            for row in result2]
            all_results = result1_list + result2_list
            return all_results
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise

    def find_node(self,
                  node_type: str,
                  node_name: str) -> List[str]:
        """Find the node in neo4j database and indicate whether it's found.

        :param node_type: type of node
        :type node_type: str
        :param node_name: name of node
        :type node_name: str
        :return: whether there is a node with the given type and name
        :rtype: List[str]
        """
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            result = session.execute_read(
                self._find_and_return_node,
                node_type,
                node_name)
            for row in result:
                logging.info(f"Found node: {row}")
            # return node if found any
            return [row for row in result]

    @staticmethod
    def _find_and_return_node(tx,
                              node_type: str,
                              node_name: str) -> List[str]:
        """The transcation function used to find the node

        :param tx: transaction function
        :type tx: unknown, Callable
        :param node_type: type of node
        :type node_type: str
        :param node_name: name of node
        :type node_name: str
        :return: List of str
        :rtype: List of str
        """
        query = (
            f"MATCH (p:{node_type}) "
            f"WHERE p.name = $node_name "
            f"RETURN p.name AS name"
        )
        result = tx.run(query,
                        node_name=node_name)
        try:
            return [row["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise


def main():
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    app = Neo4j()
    app.create_relationship(relationship="KNOWS",
                            node1_type="Person",
                            node2_type="Person",
                            node1_name="Yang",
                            node2_name="Fangfang")

    nodes = app.find_node(node_type="Person",
                          node_name="Fangfang")
    relationship = app.find_relationship(relationship="KNOWS",
                                         node1_type="Person",
                                         node2_type="Person",
                                         node1_name="Yang",
                                         node2_name="Fangfang")
    utils.display_relationship(relations=relationship)

    app.close()


if __name__ == "__main__":
    main()
