import re
import os
import time
import requests
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# TODO: Scrape images for all players

BASE_URL = 'https://www.transfermarkt.co.uk'
URLS = [
    BASE_URL + '/transfers/transferrekorde/statistik?saison_id=alle&land_id=0&ausrichtung=&spielerposition_id=&altersklasse=&leihe=&w_s=&plus=1&page=' + str(page_number)
    for page_number in range(1, 10 + 1)
]
HEADERS_LIST = [
			{
				"name": "Accept",
				"value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8"
			},
			{
				"name": "Accept-Encoding",
				"value": "gzip, deflate, br, zstd"
			},
			{
				"name": "Accept-Language",
				"value": "en-US,en;q=0.5"
			},
			{
				"name": "User-Agent",
				"value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
			}
]
HEADERS = { header['name']: header['value'] for header in HEADERS_LIST }
# Creating a session for use with every get request
s = requests.Session()
s.headers = HEADERS

def main():
    start_time = time.time()

    soups = get_all_pages_soups(URLS)
    transfer_records = []
    for soup in soups:
        transfer_data = get_transfer_data(soup)
        for record in transfer_data:
            transfer_records.append(record)
    store_data(transfer_records, 'players.csv', 'player_images')

    print(f'--- Time to execute : {time.time() - start_time}s ---')

def send_get_request(url: str) -> requests.Response:
    response = s.get(url)
    if response.status_code == 200:
        print(f'Fetched {url}')
        return response
    else:
        print(f'Failed to fetch {url}')
        print(f'Status Code: {response.status_code}')

def get_all_pages_soups(urls: list[str]) -> list[BeautifulSoup]:
    '''
    Returns a list of BeautifulSoup objects after sending get
    requests to each URL in the passed list
    '''
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_results = {
            executor.submit(get_page_soup, url): url for url in urls
        }
        soups = []
        for future in concurrent.futures.as_completed(future_results):
            soups.append(future.result())

    return soups

def get_page_soup(url: str) -> BeautifulSoup:
    '''
    Returns a BeautifulSoup object after sending a get request
    to the specified URL
    '''
    response = send_get_request(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

def get_transfer_data(soup: BeautifulSoup) -> list[dict]:
    '''
    Returns the list of transfer records after extracting data
    from the given BeautifulSoup object
    '''
    players_table = soup.find('table', {'class': 'items'})
    player_rows = players_table.find_all('tr', {'class': ['odd', 'even']})
    player_records = []
    for row in player_rows:
        player_data = parse_row(row)
        player_records.append(player_data)
    return player_records

def parse_row(row: BeautifulSoup) -> dict:
    '''
    Returns a complete record of the transfer after parsing
    the passed BeautifulSoup object of a single table row.
    '''
    cells = row.find_all('td', recursive=False)
    name_position_image = cells[1]
    age = cells[2]
    market_value = cells[3]
    season = cells[4]
    nationality = cells[5]
    old_club = cells[6]
    new_club = cells[7]
    transfer_fee = cells[8]

    transfer_data = {}
    try:
        transfer_data['player_name'] = (
            name_position_image.find('a').get_text().strip()
        )
    except:
        transfer_data['player_name'] = 'MISSING VALUE'
        print('Could not retrieve player name')
    try:
        transfer_data['player_page_url'] = (
            BASE_URL + name_position_image.find('a')['href']
        )
    except:
        transfer_data['player_page_url'] = 'MISSING VALUE'
        print('Could not retrieve player page URL')
    try:
        transfer_data['player_image_url'] = (
            name_position_image.find('img')['data-src']
        )
    except:
        transfer_data['player_image_url'] = 'MISSING VALUE'
        print('Could not retrieve player image URL')
    try:
        transfer_data['player_position'] = (
            name_position_image.find_all('tr')[1].get_text().strip()
        )
    except:
        transfer_data['player_position'] = 'MISSING VALUE'
        print('Could not retrieve player position')
    try:
        transfer_data['player_age'] = age.get_text().strip()
    except:
        transfer_data['player_age'] = 'MISSING VALUE'
        print('Could not retrieve player age')
    try:
        transfer_data['player_value_in_euros'] = market_value.get_text().strip()
    except:
        transfer_data['player_value_in_euros'] = 'MISSING VALUE'
        print('Could not retrieve player value')
    try:
        transfer_data['season'] = season.find('a').get_text().strip()
    except:
        transfer_data['season'] = 'MISSING VALUE'
        print('Could not retrieve season')
    try:
        nationalities = [
            country['title'] for country in nationality.find_all('img')
        ]
        transfer_data['player_nationalities'] = nationalities
    except:
        transfer_data['player_nationalities'] = 'MISSING VALUE'
        print('Could not retrieve player nationalities')
    try:
        old_club_info = old_club.find_all('tr')
        transfer_data['old_club_name'] = old_club_info[0].find('a')['title']
    except:
        transfer_data['old_club_name'] = 'MISSING VALUE'
        print('Could not retrieve old club info')
    try:
        transfer_data['old_league_name'] = old_club_info[1].find('a')['title']
    except:
        transfer_data['old_league_name'] = 'MISSING VALUE'
        print('Could not retrieve old club info')
    try:
        new_club_info = new_club.find_all('tr')
        transfer_data['new_club_name'] = new_club_info[0].find('a')['title']
    except:
        transfer_data['new_club_name'] = 'MISSING VALUE'
        print('Could not retrieve new club info')
    try:
        transfer_data['new_league_name'] = new_club_info[1].find('a')['title']
    except:
        transfer_data['new_league_name'] = 'MISSING VALUE'
        print('Could not retrieve new club info')
    try:
        transfer_data['transfer_fee_in_euros'] = transfer_fee.find('a').get_text().strip()
    except:
        transfer_data['transfer_fee_in_euros'] = 'MISSING VALUE'
        print('Could not retrieve transfer fee')
    return transfer_data

def get_image_filename(image_url: str, player_name: str) -> str:
    '''
    Returns the filename that should be used for the image.
    Filename is determined by concatenating players name and
    the file extension extracted with re from the given URL
    '''
    regex = re.compile(r'(\.[a-zA-Z]{3,4})(?=\?lm=1)')
    match = regex.search(image_url)
    if match:
        file_extension = match[1].lower()
        filename = player_name + file_extension
        return filename
    else:
        print(f"There was an error while finding {player_name} image's filename")
        return f'{player_name}_unknown_extension.jpg'



def download_images(records: list[dict]) -> None:
    '''
    Scrapes the images for each player in the provided list of
    records and then appends them in-place to each of the dictionary
    '''
    for record in records:
        response = send_get_request(record['player_image_url'])
        record['player_image'] = {
            'data': response.content,
            'filename': get_image_filename(
                record['player_image_url'], record['player_name']
            )
        }

def store_images(records: list[dict], dir_name: str) -> bool:
    '''
    Stores images according to player names in the specified directory
    name in the current path
    '''
    try:
        dir_path = os.path.join(os.path.curdir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        download_images(records)
        for record in records:
            image_data = record['player_image']['data']
            image_filename = record['player_image']['filename']
            try:
                with open(os.path.join(dir_path, image_filename), 'wb') as file:
                    file.write(image_data)
            except:
                print(f'Error while writing to image file: {image_filename}')
        return True
    except:
        return False

def store_in_csv(records: list[dict], filepath: str) -> bool:
    '''
    Applies some transformations to the given list of records, sorts
    it according to the transfer fee and then stores it in a csv file
    '''
    try:
        df = pd.DataFrame.from_dict(records)
        # Dropping images as they have already been written on disk
        df.drop(columns=['player_image'], inplace=True)
        # Transforming values like "€100.23m" into "100230000"
        df['player_value_in_euros'] = (df['player_value_in_euros']
                .str.replace('€', '')
                .str.replace('.', '')
                .str.replace('m', '0000')
        )
        df['transfer_fee_in_euros'] = (df['transfer_fee_in_euros']
                .str.replace('€', '')
                .str.replace('.', '')
                .str.replace('m', '0000')
        )
        # Converting transfer fees to numeric so sorting
        # is done correctly
        df['transfer_fee_in_euros'] = pd.to_numeric(
            df['transfer_fee_in_euros'], errors='coerce'
        )
        df.sort_values('transfer_fee_in_euros', ascending=False, inplace=True)
        df.index = range(1, len(df) + 1)
        df.index.name = 'transfer_id'

        df.to_csv(filepath, index=True)
        return True
    except:
        return False
    
def store_data(records: list[dict], csv_filename: str, images_dir_name: str):
    if store_images(records, images_dir_name):
        print('Images have been written to disk')
    else:
        print('There was an error while writing images to disk')
    if store_in_csv(records, csv_filename):
        print('Data has been written to csv')
    else:
        print('There was an error while writing data to csv')


if __name__ == '__main__':
    main()