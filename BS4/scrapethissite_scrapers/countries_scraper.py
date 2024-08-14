from bs4 import BeautifulSoup, Tag
import requests
import pandas as pd

def get_country_info(tag_name: str, attributes: dict) -> str:
    info = (
        div.find(tag_name, attributes)
        .get_text()
        .strip()
    )
    return info


TARGET_URL = 'https://www.scrapethissite.com/pages/simple/'

html = requests.get(TARGET_URL)
soup = BeautifulSoup(html.content, 'html.parser')

country_divs = soup.findAll('div', {'class': 'col-md-4 country'})

country_infos = []

for div in country_divs:
    country_name = get_country_info('h3', {'class': 'country-name'})
    country_area_km2 = get_country_info('span', {'class': 'country-area'})
    country_capital = get_country_info('span', {'class': 'country-capital'})
    country_population = get_country_info('span', {'class': 'country-population'})
    country_data = {
        'country_name': country_name,
        'country_capital': country_capital,
        'country_area_km2': country_area_km2,
        'country_population': country_population
    }
    country_infos.append(country_data)

df = pd.DataFrame.from_dict(country_infos)

try:
    df.to_excel('countries.xlsx', sheet_name='countries')
    print('Values have been written to excel file')
except FileNotFoundError:
    print('Excel file does not exist')