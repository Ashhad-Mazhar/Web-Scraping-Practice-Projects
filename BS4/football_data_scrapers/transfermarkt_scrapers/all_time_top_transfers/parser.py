from config import BASE_URL
from bs4 import BeautifulSoup

class TransferParser:
    def parse(self, html: str) -> list[dict]:
        '''
        Returns the list of transfer records after extracting data
        from the given BeautifulSoup object
        '''
        soup = BeautifulSoup(html, 'html.parser')
        players_table = soup.find('table', {'class': 'items'})
        player_rows = players_table.find_all('tr', {'class': ['odd', 'even']})
        all_data = []
        for row in player_rows:
            player_data = self.parse_row(row)
            all_data.append(player_data)
        return all_data
    
    def parse_row(self, row: BeautifulSoup) -> dict:
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