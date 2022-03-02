from brain import Database


def get_text():
    query = '''
            SELECT CONVERT(old_text USING utf8) 
            FROM text 
            WHERE old_id=1071857811;
            '''
    database = Database()
    result = database.query(query=query)
    return result