import os

BASE_URL = 'https://www.transfermarkt.co.uk'

# Query parameters
# 'alle' means (to the server) that we need all seasons' data
SEASON_ID = 'alle'

# The URL for the page excluding the page number parameter that
# will be dynamically filled in by the scraper module
TRANSFER_PAGE_URL = BASE_URL + f'/transfers/transferrekorde/statistik/top/ajax/yw2/saison_id/{SEASON_ID}/land_id//ausrichtung//spielerposition_id//altersklasse//jahrgang/0/leihe//w_s//plus/1/galerie/0/page/'

# The paths where the scraped files will be stored
if SEASON_ID == 'alle':
	CSV_FILE_PATH = os.path.join('All_Seasons', f'players.csv')
	IMAGES_PATH = os.path.join('All_Seasons', f'player_images')
else:
	CSV_FILE_PATH = os.path.join(SEASON_ID, 'players.csv')
	IMAGES_PATH = os.path.join(SEASON_ID, 'player_images')

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
# Converting headers copied from the browser to a single dictionary
HEADERS = { header['name']: header['value'] for header in HEADERS_LIST }