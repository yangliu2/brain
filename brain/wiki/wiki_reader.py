from brain import Database
import mwparserfromhell
import wikitextparser as wtp
import json
import importlib.resources


class WikiParser:

    def __init__(self,
                 keyword: str,
                 database: str = 'wiki_en') -> None:
        self.database = Database(database=database)
        self.keyword = keyword

        # get keyword id cache, supposely
        cache_file = 'wiki/data/keyword_id.json'
        self.cache_path = importlib.resources.files("brain") / cache_file
        self.get_keyword_ids()

    def get_keyword_ids(self):
        ''' Get the keyword id from the cache file '''
        if self.cache_path.exists():
            with self.cache_path.open('r') as f:
                self.keyword_ids = json.load(f)
        else:
            with self.cache_path.open('w') as f:
                self.keyword_ids = {}
                json.dump(self.keyword_ids, f)

    def cache_keyword_id(self):
        ''' Cache the keyword id to the keyword_id.json file '''
        if self.cache_path.exists():
            with self.cache_path.open('w') as f:
                json.dump(self.keyword_ids, f)

    def get_keyword_id(self):
        ''' Get the keyword id from the database '''
        query = """
                SELECT page_latest
                FROM page
                WHERE page_title like %s;
                """

        result = self.database.query(query=query,
                                     params=(self.keyword,))

        # cache the keyword id
        self.keyword_ids[self.keyword] = result[0][0]
        self.cache_keyword_id()
        return result[0][0]

    def get_wiki_text(self):
        ''' Get the wiki format text from the database '''

        # get the keyword id
        if self.keyword in self.keyword_ids:
            keyword_id = self.keyword_ids[self.keyword]
        else:
            keyword_id = self.get_keyword_id()

        # query the database
        query = '''
                SELECT CONVERT(old_text USING utf8) 
                FROM text 
                WHERE old_id=%s;
                '''
        result = self.database.query(query=query,
                                     params=(keyword_id,))
        return result[0][0]

    def remove_extra_formatting(self, text: str) -> str:
        extra_sections = ['References', 'External links', 'See also',
                          'Further reading', 'Notes']
        return text

    @staticmethod
    def parse_wiki_text(text: str) -> str:
        ''' Parse the wiki text to plain text '''
        wiki_text = mwparserfromhell.parse(text)
        plain_text = wiki_text.strip_code()
        return plain_text

    def get_text(self):
        ''' Convert the wiki format text to plain text '''

        wiki_text = self.get_wiki_text()

        # Put the wiki text in sectios, and filter out the extra sections
        sectioned_text = wtp.parse(wiki_text)
        extra_sections = ['References', 'External links', 'See also',
                          'Further reading', 'Notes', 'Maps']
        parsed_sections = [self.parse_wiki_text(str(x))
                           for x in sectioned_text.sections
                           if not x.title or 
                               x.title.strip() not in extra_sections]

        plain_text = " ".join(parsed_sections)
        stripped_text = plain_text.replace("\n", " ")

        return stripped_text


def main():

    keyword = 'China'
    # wiki database like searches requires a CamelCase string
    parser = WikiParser(keyword=keyword.title())
    result = parser.get_text()
    print(result)


if __name__ == '__main__':
    main()
