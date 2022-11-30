from neo4j import GraphDatabase
from loguru import logger
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
                logger.info(f"Created node {row['n']}")

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
            logger.error(f"{query} raised an error: \n {exception}")
            raise

    def create_edge(self,
                    edge: str,
                    node1_type: str,
                    node2_type: str,
                    node1_name: str,
                    node2_name: str):
        """Create a relationship with two nodes. The relationship is 
        unidirectional. If the relationship alread exist, then choose to 
        strenthen the relationship. 

        :param edge: indicate the relaitonship between two nodes. This
        string is normally all caps to indicate it's a relationship
        :type edge: str
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
        found_edge = self.find_edge(edge=edge,
                                    node1_type=node1_type,
                                    node2_type=node2_type,
                                    node1_name=node1_name,
                                    node2_name=node2_name)
        if not found_edge:
            with self.driver.session(
                    database=Neo4jEnums.NEO4J.value) as session:
                # Write transactions allow the driver to handle retries and
                #  transient errors
                result = session.execute_write(
                    self._create_and_return_edge,
                    edge,
                    node1_type,
                    node2_type,
                    node1_name,
                    node2_name)
                for row in result:
                    logger.info(f"Created {edge} between: "
                                 f"{row['n1']}, {row['n2']}")
        else:
            # get confidence and modify it if relationship exists
            confidence = float(found_edge[0]['confidence'])
            new_confidence = self.calculate_confidence(confidence=confidence)
            with self.driver.session(
                    database=Neo4jEnums.NEO4J.value) as session:
                # Write transactions allow the driver to handle retries and
                #  transient errors
                result = session.execute_write(
                    self._modify_edge,
                    edge,
                    node1_type,
                    node2_type,
                    node1_name,
                    node2_name,
                    new_confidence)
                for row in result:
                    logger.info(f"Relationship {edge} was strenthened "
                                 f"between {node1_name} and {node2_name}")

    @staticmethod
    def _create_and_return_edge(tx,
                                edge: str,
                                node1_type: str,
                                node2_type: str,
                                node1_name: str,
                                node2_name: str,
                                confidence: float = 0.5) -> List[Dict]:
        """Actually create the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param edge: how node1 is related to node 2, all caps to 
        indicate relationship
        :type edge: str
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
            f"CREATE (n1)-[r: {edge} "
            f"{{ confidence: {confidence} }}]->(n2) "
            f"RETURN n1, n2"
        )

        result = tx.run(query)
        try:
            return [{"n1": row["n1"]["name"], "n2": row["n2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logger.error(f"{query} raised an error: \n {exception}")
            raise

    @staticmethod
    def calculate_confidence(confidence: float,
                             increase_factor: float = 0.10) -> float:
        """Calculate the new relationship confidence if the relationship 
        already exists

        :param confidence: old confidence
        :type confidence: float
        :param increase_factor: how much does the confidence increase as a 
        factor, defaults to 0.10
        :type increase_factor: float, optional
        :return: new confidence used to update
        :rtype: float
        """
        new_confidence = confidence + (1 - confidence) * increase_factor
        return round(new_confidence, 3)

    def _modify_edge(self,
                     tx,
                     edge: str,
                     node1_type: str,
                     node2_type: str,
                     node1_name: str,
                     node2_name: str,
                     confidence: float) -> List[Dict]:
        """Actually modify the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param edge: how node1 is related to node 2, all caps to 
        indicate relationship
        :type edge: str
        :param node1_type: type for node 1, cap first letter
        :type node1_type: str
        :param node2_type: type of node 2, cap the first letter
        :type node2_type: str
        :param node1_name: name for node 1
        :type node1_name: str
        :param node2_name: name for node 2
        :type node2_name: str
        :param confidence: confidence of the relationship
        :type confidence: float
        :return: List of dict 
        :rtype: List of Dict
        """
        query = (
            f"MATCH (n1: {node1_type} {{ name: '{node1_name}' }}) "
            f"-[r:{edge}]->"
            f"(n2: {node2_type} {{ name: '{node2_name}'}}) "
            f"SET r.confidence = {confidence} "
            f"RETURN n1, n2"
        )

        result = tx.run(query)
        try:
            return [{"n1": row["n1"]["name"], "n2": row["n2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logger.error(f"{query} raised an error: \n {exception}")
            raise

    def find_edge(self,
                  edge: str,
                  node1_type: str,
                  node2_type: str,
                  node1_name: str,
                  node2_name: str) -> List[Dict[str, str]]:
        """Find a relationship with two nodes. The relationship is 
        unidirectional.

        :param edge: indicate the relaitonship between two nodes. This
        string is normally all caps to indicate it's a relationship
        :type edge: str
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
                self._find_edge,
                edge,
                node1_type,
                node2_type,
                node1_name,
                node2_name)
            for row in result:
                logger.info(f"Found relationship({edge}) between: "
                             f"{row['n1']}, {row['n2']}")

            # return relationships if found any
            return [row for row in result]

    @staticmethod
    def _find_edge(tx,
                   edge: str,
                   node1_type: str,
                   node2_type: str,
                   node1_name: str,
                   node2_name: str) -> List[Dict]:
        """Actually find the relationship in a transaction function 

        :param tx: the transaction function
        :type tx: unknown, probably a Callable
        :param edge: how node1 is related to node 2, all caps to 
        indicate relationship
        :type edge: str
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
            f"MATCH (n1: {node1_type})-[r:{edge}]->(n2:{node2_type}) "
            f"WHERE n1.name = '{node1_name}' AND n2.name = '{node2_name}' "
            f"RETURN n1, n2, r"
        )
        result = tx.run(query)
        try:
            return [{"n1": row["n1"]["name"],
                     "n2": row["n2"]["name"],
                     "r": edge,
                     "confidence": row["r"]["confidence"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logger.error(f"{query} raised an error: \n {exception}")
            raise

    def find_all_edge(self,
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
                self._find_all_edge,
                node_type,
                node_name)
            for row in result:
                logger.info(f"Found relationship({row['r']}) between: "
                             f"{row['n1']}, {row['n2']}")

            # return relationships if found any
            return [row for row in result]

    @staticmethod
    def _find_all_edge(tx,
                       node_type: str,
                       node_name: str) -> List[Dict]:
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
        if node_type:
            # get all relationships originated to the node
            query = (
                f"MATCH(n1: {node_type} {{name: '{node_name}'}})-[r]->(n2) "
                f"RETURN n1, r, n2"
            )
            result1 = tx.run(query)

            # get all relationships directed towards the node
            query = (
                f"MATCH(n1)-[r]->(n2:{node_type} {{name: '{node_name}'}}) "
                f"RETURN n1, r, n2"
            )
        else:
            # get all relationships originated to the node
            query = (
                f"MATCH(n1 {{name: '{node_name}'}})-[r]->(n2) "
                f"RETURN n1, r, n2"
            )
            result1 = tx.run(query)

            # get all relationships directed towards the node
            query = (
                f"MATCH(n1)-[r]->(n2 {{name: '{node_name}'}}) "
                f"RETURN n1, r, n2"
            )

        result2 = tx.run(query)

        try:
            result1_list = [{"n1": row["n1"]["name"],
                             "r": str(row['r'].type),
                             "c": row['r']['confidence'],
                             "n2": row["n2"]["name"]}
                            for row in result1]
            result2_list = [{"n1": row["n1"]["name"],
                             "r": str(row['r'].type),
                             "c": row['r']['confidence'],
                             "n2": row["n2"]["name"]}
                            for row in result2]
            all_results = result1_list + result2_list
            return all_results
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logger.error(f"{query} raised an error: \n {exception}")
            raise

    def find_node(self,
                  node_name: str,
                  node_type: str = None) -> List[str]:
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
                logger.info(f"Found node: {row}")
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
        if node_type:
            query = (
                f"MATCH (p:{node_type}) "
                f"WHERE p.name = $node_name "
                f"RETURN p.name AS name"
            )
        else:
            query = (
                f"MATCH (p) "
                f"WHERE p.name = $node_name "
                f"RETURN p.name AS name"
            )
        result = tx.run(query,
                        node_name=node_name)
        try:
            return [row["name"] for row in result]
        except ServiceUnavailable as exception:
            logger.error(f"{query} raised an error: \n {exception}")
            raise


def main():
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    app = Neo4j()
    app.create_edge(edge="KNOWS",
                    node1_type="Person",
                    node2_type="Person",
                    node1_name="Yang",
                    node2_name="Fangfang")

    nodes = app.find_node(node_type="Person",
                          node_name="Fangfang")
    edge = app.find_edge(edge="KNOWS",
                         node1_type="Person",
                         node2_type="Person",
                         node1_name="Yang",
                         node2_name="Fangfang")
    utils.display_edge(edges=edge)

    app.close()


if __name__ == "__main__":
    logger.add("Neo4j.log")
    main()
