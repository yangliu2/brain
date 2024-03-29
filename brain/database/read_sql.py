""" make a class that connects to the database """

import mysql.connector as mysqlConnector


class Database:
    def __init__(self,
                 host: str = "localhost",
                 user: str = "root",
                 password: str = "example",
                 database: str = "test"):
        self.conn = mysqlConnector.connect(host=host,
                                           user=user,
                                           passwd=password,
                                           database=database)

         # Checking if connection is made or not
        if self.conn:
            print("Connection Successful :)")
        else:
            print("Connection Failed :(")

    def query(self,
              query: str, 
              params: tuple = None
              ) -> None:
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
        except Exception as e:
            print("Invalid Query")
            print(e)
            result = None

        cursor.close()
        return result
