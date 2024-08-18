import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

# TODO: Implement async requests,
# scrape images for all players

BASE_URL = 'https://www.transfermarkt.co.uk'
URLS = [
    BASE_URL + '/transfers/transferrekorde/statistik?saison_id=alle&land_id=0&ausrichtung=&spielerposition_id=&altersklasse=&leihe=&w_s=&plus=1&page=' + str(page_number)
    for page_number in range(1, 10 + 1)
]
HEADERS = {
        'Host': 'www.transfermarkt.co.uk',
        'User-Agent': 'WebSniffer/1.2 (+http://websniffer.com/)',
        'Accept': '*/*',
        'Referer': 'https://websniffer.com/'
}
# Creating a session for use with every get request
s = requests.Session()
s.headers = HEADERS
s.get(URLS[0])

def main():
    start_time = time.time()

    soups = get_all_pages_soups(URLS)
    transfer_records = []
    for soup in soups:
        transfer_data = get_transfer_data(soup)
        for record in transfer_data:
            transfer_records.append(record)
    if store_in_csv(transfer_records, 'players.csv'):
        print('Data has been written to csv')
    else:
        print('There was an error while writing data to csv')

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
    soups = []
    for url in urls:
        soup = get_page_soup(url)
        soups.append(soup)
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
    
def store_in_csv(records: list[dict], filepath: str) -> bool:
    '''
    Applies some transformations to the given list of records, sorts
    it according to the transfer fee and then stores it in a csv file
    '''
    try:
        df = pd.DataFrame.from_dict(records)

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


if __name__ == '__main__':
    main()