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

    store_in_csv(turtle_records, 'turtles.csv')


def get_soup_object(url: str) -> BeautifulSoup:
    '''
    Returns a BeautifulSoup object after sending a request
    to the given URL
    '''   
    response = requests.get(url)
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

def store_in_csv(records: list[dict], filename: str) -> None:
    '''
    Stores a list of dictionaries in a csv file on disk
    '''
    df = pd.DataFrame.from_dict(records)
    df.index = range(1, len(df) + 1)
    df.index.name = 'record_id'
    df.to_csv('turtles.csv', index=True)


if __name__ == '__main__':
    main()