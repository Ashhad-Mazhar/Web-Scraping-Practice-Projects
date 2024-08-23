import httpx
import utils
import asyncio
from parser import TransferParser
from config import HEADERS, TRANSFER_PAGE_URL, MAXIMUM_PAGES

class TransferScraper:
    '''
    Meant to handle communication with the server
    '''
    def __init__(self) -> None:
        '''
        Creates a session to be used throughout the program and
        includes the headers from the config file
        '''
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=None)
    
    async def scrape(self) -> list[dict]:
        '''
        Returns a list of records obtained after parsing all
        URLs
        '''
        parser = TransferParser()
        all_data = []
        previous_html = None
        for page_number in range(1, MAXIMUM_PAGES + 1):
            url = TRANSFER_PAGE_URL + str(page_number)
            current_html = await self.fetch_url(url)

            if previous_html is not None and current_html == previous_html:
                print(f'All pages scraped.')
            
            all_data.extend(parser.parse(current_html))
            
            previous_html = current_html
        await self.download_images(all_data)
        return all_data
    
    async def fetch_url(self, url: str) -> httpx.Response.content:
        '''
        Sends a GET request to the specified URL and returns the
        body of the response in case the request is successful
        and returns None otherwise
        '''
        response = await self.client.get(url)
        if response.status_code == 200:
            print(f'Fetched {url}')
            return response.content
        else:
            print(f'Could not fetch {url}')
            print(f'Status Code: {response.status_code}')
            return None
        
    async def download_images(self, records: list[dict]) -> None:
        '''
        Scrapes the images for each player in the provided list of
        records and then appends them in-place to each of the dictionary
        '''
        async def download_image(record: dict) -> None:
            record['player_image'] = {
                'data': await self.fetch_url(record['player_image_url']),
                'filename': utils.get_image_filename(
                    record['player_image_url'], record['player_name']
                )
            }
            await asyncio.sleep(0.5)
        
        tasks = [download_image(record) for record in records]
        await asyncio.gather(*tasks)