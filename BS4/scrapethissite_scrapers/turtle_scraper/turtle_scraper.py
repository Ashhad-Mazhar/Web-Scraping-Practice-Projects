import re
import requests
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

'''
This script scrapes info about turtles from the given page by
finding the source of the iframe containing the info and then
following links on the obtained page to get info about all
turtles.
It also stores images scraped from the page according to the
turtle names.
'''

def main():
    BASE_URL = 'https://www.scrapethissite.com'
    STARTING_URL = 'https://www.scrapethissite.com/pages/frames/'

    starting_url_soup = get_soup_object(STARTING_URL)
    iframe_srcs = starting_url_soup.find_all('iframe', {'id': 'iframe'})
    if len(iframe_srcs) != 1:
        print('Number of iframes on this website has changed.')
        print('Please update your script.')
        exit()
    else:
        iframe_src = iframe_srcs[0]['src']

    turtle_page_urls = get_all_turtle_urls(BASE_URL + iframe_src, BASE_URL)
    turtle_soups = get_all_pages_soups(turtle_page_urls)

    turtle_records = []
    for turtle_soup in turtle_soups:
        record = get_turtle_info(turtle_soup)
        turtle_records.append(record)

    download_all_turtle_images(turtle_records)
    store_data(turtle_records, 'turtles.csv')


def make_request(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    }
    response = requests.get(url, headers=headers)
    return response

def get_soup_object(url: str) -> BeautifulSoup:
    '''
    Returns a BeautifulSoup object after sending a request
    to the given URL
    '''   
    response = make_request(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_all_pages_soups(urls: list[str]) -> BeautifulSoup:
    '''
    Executes 4 async threads to make requests to all pages
    and returns their BeautifulSoup objects
    '''
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_results = {
            executor.submit(get_soup_object, url): url for url in urls
        }
        soup_objects = []
        for future in concurrent.futures.as_completed(future_results):
            soup_objects.append(future.result())
            print(f'{future_results[future]} has been scraped')
    return soup_objects

def get_all_turtle_urls(page_url: str, base_url: str) -> list[str]:
    '''
    Returns all URLs present on the given page
    '''
    soup = get_soup_object(page_url)
    turtle_cards = soup.find_all('div', {'class': 'col-md-4 turtle-family-card'})
    turtle_urls = []
    for turtle_card in turtle_cards:
        href = turtle_card.find('a', {'class': 'btn btn-default btn-xs'})['href']
        url = base_url + href
        turtle_urls.append(url)
    return turtle_urls

def get_turtle_info(soup: BeautifulSoup) -> dict:
    '''
    Returns a dictionary representing a complete record extracted
    from the given page passed to the function as a BeautifulSoup
    object
    '''

    # The div containing the info
    turtle_div = soup.find(
        'div',
        {'class': 'col-md-6 col-md-offset-3 turtle-family-detail'}
    )
    info = {}
    info['family_name'] = (turtle_div
                           .find('h3', {'class': 'family-name'})
                           .get_text().strip())
    info['image_url'] = (turtle_div
                         .find('img', {'class': 'turtle-image center-block'})
                         ['src'])
    # The paragraph to be parsed with regex
    paragraph_tag = turtle_div.find('p', {'class': 'lead'})
    info['common_name'] = (paragraph_tag
                           .find('strong', {'class': 'common-name'})
                           .get_text().strip())
    # Extracting year of discovery and discoverer through regex
    regex = re.compile(r'(\d{4}) by (.+)\.')
    regex_match = regex.search(paragraph_tag.text)
    if regex_match:
        info['discovery_year'] = regex_match.group(1)
        info['discoverer'] = regex_match.group(2)
    return info

def download_turtle_image(record: dict) -> bool:
    '''
    Downloads image for the given record and saves it in the
    given dictionary which has been passed by reference.
    '''
    response = make_request(record['image_url'])
    if response.status_code == 200:
        record['image_data'] = response.content
        return True
    else:
        print(f'Error Code: {response.status_code}')
        return False


def download_all_turtle_images(records: list[dict]):
    '''
    Creates 4 async threads to download images for all the records
    in the list which has been passed by reference.
    '''
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_results = {
            executor.submit(download_turtle_image, record): record['image_url']
            for record in records
        }
        for future_result in concurrent.futures.as_completed(future_results):
            if future_result.result():
                print(f'{future_results[future_result]} has been downloaded.')
            else:
                print(f'Error while downloading {future_results[future_result]}')


def store_data(records: list[dict], filename: str) -> None:
    '''
    Stores a list of dictionaries in a csv file on disk
    '''
    df = pd.DataFrame.from_dict(records)
    df.index = range(1, len(df) + 1)
    df.index.name = 'record_id'

    for record_id, row in df.iterrows():
        image_file_name = f'{row['family_name']}.jpg'
        image_data = row['image_data']
        with open(image_file_name, 'wb') as file:
            file.write(image_data)

    df.drop(columns=['image_data'], inplace=True)
    df.to_csv(filename, index=True)


if __name__ == '__main__':
    main()