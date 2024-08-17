import requests
from bs4 import BeautifulSoup

'''
This script is meant for practicing spoofing headers. The target
page does not return the required content unless the correct headers
are provided with the request.
'''

URL = 'https://www.scrapethissite.com/pages/advanced/?gotcha=headers'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8'
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

message = soup.find('div', 'col-md-4 col-md-offset-4')
print(message.get_text().strip())