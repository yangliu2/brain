from brain import Database
import mwparserfromhell


class WikiParser:

    def __init__(self,
                 query: str,
                 database: str = 'wiki_en') -> None:
        self.database = database
        self.query = query

    def get_wiki_text(self):
        ''' Get the wiki format text from the database '''

        query = '''
                SELECT CONVERT(old_text USING utf8) 
                FROM text 
                WHERE old_id=1071857811;
                '''
        database = Database(database=self.database)
        result = database.query(query=self.query)
        return result

    def get_text(self):
        ''' Convert the wiki format text to plain text '''

        wiki_text = self.get_text()
        parsed_wikicode = mwparserfromhell.parse(wiki_text)
        read_text = parsed_wikicode.strip_code()
        return read_text

def main():
    ''' Main function '''

    query = '''
            SELECT CONVERT(old_text USING utf8) 
            FROM text 
            WHERE old_id=1071857811;
            '''
    database = Database(database='wiki_en')
    result = database.query(query=query)
    print(result)

if __name__ == '__main__':
    main()