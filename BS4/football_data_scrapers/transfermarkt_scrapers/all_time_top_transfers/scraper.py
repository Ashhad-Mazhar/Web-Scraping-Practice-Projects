import requests
import concurrent.futures
from config import URLS, HEADERS
from parser import TransferParser
from concurrent.futures import ThreadPoolExecutor

class TransferScraper:
    '''
    Meant to handle communication with the server
    '''
    def __init__(self) -> None:
        '''
        Creates a session to be used throughout the program and
        includes the headers from the config file
        '''
        self.session = requests.session()
        self.session.headers.update(HEADERS)
    
    def fetch_url(self, url: str) -> requests.Response.content:
        '''
        Sends a GET request to the specified URL and returns the
        body of the response in case the request is successful
        and returns None otherwise
        '''
        response = self.session.get(url)
        if response.status_code == 200:
            print(f'Fetched {url}')
            return response.content
        else:
            print(f'Could not fetch {url}')
            print(f'Status Code: {response.status_code}')
            return None
    
    def scrape(self) -> list[dict]:
        '''
        Returns a list of records obtained after parsing all
        URLs
        '''
        parser = TransferParser()
        all_data = []
        for url in URLS:
            html = self.fetch_url(url)
            if html:
                page_data = parser.parse(html)
                all_data.extend(page_data)
        return all_data