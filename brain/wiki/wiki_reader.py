from brain import Database
import mwparserfromhell


class WikiParser:

    def __init__(self,
                 database: str,
                 query: str) -> None:
        self.database = database


    def get_text(self, 
                 query: str):
        query = '''
                SELECT CONVERT(old_text USING utf8) 
                FROM text 
                WHERE old_id=1071857811;
                '''
        database = Database(database=self.database)
        result = database.query(query=query)
        return result

    def convert_wiki_to_text(self):
        wiki_text = self.get_text()
        parsed_wikicode = mwparserfromhell.parse(wiki_text)
        read_text = parsed_wikicode.strip_code()
        return read_text