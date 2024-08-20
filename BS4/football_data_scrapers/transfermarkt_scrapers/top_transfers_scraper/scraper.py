import utils
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
    
    def scrape(self) -> list[dict]:
        '''
        Returns a list of records obtained after parsing all
        URLs
        '''
        parser = TransferParser()
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_results = {
                executor.submit(self.fetch_url, url): url for url in URLS
            }
            all_htmls = []
            for future in concurrent.futures.as_completed(future_results):
                all_htmls.append(future.result())
            all_data = []
            for html in all_htmls:
                if html:
                    page_data = parser.parse(html)
                    all_data.extend(page_data)
            self.download_images(all_data)
        return all_data
    
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
        
    def download_images(self, records: list[dict]) -> None:
        '''
        Scrapes the images for each player in the provided list of
        records and then appends them in-place to each of the dictionary
        '''
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_results = {
                executor.submit(
                    self.fetch_url, record['player_image_url']): record
                    for record in records
            }
            for future in concurrent.futures.as_completed(future_results):
                image_data = future.result()
                record = future_results[future]
                record['player_image'] = {
                    'data': image_data,
                    'filename': utils.get_image_filename(
                        record['player_image_url'], record['player_name']
                    )
                }