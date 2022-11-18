from neo4j import GraphDatabase
import logging
from pathlib import Path
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

    def create_friendship(self,
                          person1_name: str,
                          person2_name: str):
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            # Write transactions allow the driver to handle retries and
            #  transient errors
            result = session.execute_write(
                self._create_and_return_friendship,
                person1_name,
                person2_name)
            for row in result:
                print(f"Created friendship between: {row['p1']}, {row['p2']}")

    @staticmethod
    def _create_and_return_friendship(tx,
                                      person1_name: str,
                                      person2_name: str):
        # To learn more about the Cypher syntax,
        #  see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords
        #  https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query,
                        person1_name=person1_name,
                        person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(f"{query} raised an error: \n {exception}")
            raise

    def find_person(self,
                    person_name: str):
        with self.driver.session(database=Neo4jEnums.NEO4J.value) as session:
            result = session.execute_read(
                self._find_and_return_person,
                person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx,
                                person_name: str):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]


def main():
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    app = Neo4j()
    app.create_friendship("Alice", "David")
    app.find_person("Alice")
    app.close()


if __name__ == "__main__":
    main()
