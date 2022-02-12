""" Generic scraper to get information"""

from bs4 import BeautifulSoup

class Scraper:
    def __init__(self,
                 url: str):
        self.url = url

    def pull(self):
        """
        Get the relevant information needed
        :return:
        """
        pass
