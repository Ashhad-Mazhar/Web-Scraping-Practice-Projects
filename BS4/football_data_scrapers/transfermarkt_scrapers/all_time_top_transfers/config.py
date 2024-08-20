BASE_URL = 'https://www.transfermarkt.co.uk'
# Query parameters
# 'alle' means (to the server) that we need all seasons' data
SEASON_ID = 'alle'
NUMBER_OF_PAGES = 10
# List of URLS to scrape
URLS = [
    BASE_URL + f'/transfers/transferrekorde/statistik?saison_id={SEASON_ID}&land_id=0&ausrichtung=&spielerposition_id=&altersklasse=&leihe=&w_s=&plus=1&page={str(page_number)}'
    for page_number in range(1, NUMBER_OF_PAGES + 1)
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
# Converting headers copied from the browser to a single dictionary
HEADERS = { header['name']: header['value'] for header in HEADERS_LIST }

CSV_FILENAME = 'players.csv'
IMAGES_PATH = 'player_images'