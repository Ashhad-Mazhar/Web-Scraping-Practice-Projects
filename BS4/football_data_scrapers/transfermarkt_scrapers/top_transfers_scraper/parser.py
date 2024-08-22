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
    
    def safe_extract(
            self,
            function: callable,
            error_message: str,
            default_value:str='MISSING VALUE'
    ) -> str:
        '''
        Executes the given function and returns its result. In
        case of an expection, returns the default value and prints
        an error message to the terminal
        '''
        try:
            return function()
        except Exception as e:
            print(error_message)
            return default_value

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
        transfer_data['player_name'] = self.safe_extract(
            lambda: name_position_image.find('a').get_text().strip(),
            'Could not retrieve player name'
        )
        transfer_data['player_page_url'] = self.safe_extract(
            lambda: BASE_URL + name_position_image.find('a')['href'],
            'Could not retrieve player page URL'
        )
        transfer_data['player_image_url'] = self.safe_extract(
            lambda: name_position_image.find('img')['data-src'],
            'Could not retrieve player image URL'
        )
        transfer_data['player_position'] = self.safe_extract(
            lambda: name_position_image.find_all('tr')[1].get_text().strip(),
            'Could not retrieve player position'
        )
        transfer_data['player_age'] = self.safe_extract(
            lambda: age.get_text().strip(),
            'Could not retrieve player age'
        )
        transfer_data['player_value_in_euros'] = self.safe_extract(
            lambda: market_value.get_text().strip(),
            'Could not retrieve player value'
        )
        transfer_data['season'] = self.safe_extract(
            lambda: season.find('a').get_text().strip(),
            'Could not retrieve transfer season'
        )
        transfer_data['player_nationalities'] = self.safe_extract(
            lambda: [country['title'] for country in nationality.find_all('img')],
            'Could not retrieve player nationalities'
        )
        old_club_info = self.safe_extract(
            lambda: old_club.find_all('tr'),
            'Could not retrieve old club data'
        )
        transfer_data['old_club_name'] = self.safe_extract(
            lambda: old_club_info[0].find('a')['title'],
            'Could not retrieve old club name'
        )
        transfer_data['old_league_name'] = self.safe_extract(
            lambda: old_club_info[1].find('a')['title'],
            'Could not retrieve old league name'
        )
        new_club_info = self.safe_extract(
            lambda: new_club.find_all('tr'),
            'Could not retrieve new club info'
        )
        transfer_data['new_club_name'] = self.safe_extract(
            lambda: new_club_info[0].find('a')['title'],
            'Could not retrieve new club name'
        )
        transfer_data['new_league_name'] = self.safe_extract(
            lambda: new_club_info[1].find('a')['title'],
            'Could not retrieve new league name'
        )
        transfer_data['transfer_fee_in_euros'] = self.safe_extract(
            lambda: transfer_fee.find('a').get_text().strip(),
            'Could not retrieve transfer fee'
        )
        return transfer_data