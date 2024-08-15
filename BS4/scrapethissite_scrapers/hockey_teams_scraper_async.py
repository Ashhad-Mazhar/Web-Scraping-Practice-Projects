import time
import requests
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

'''
Asynchronous implementation of the hockey teams scraper.
Uses four workers to scrape multiple pages at once.

Synchronous execution time: 66.34s
Asynchronous execution time: 14.55s
'''

def check_page_validity(soup_object: BeautifulSoup) -> bool:
    '''
    Checks to see if the given page has any team entries in the
    table. No entries in the table other than the header row means
    that the page is invalid.
    '''
    data_table = soup_object.find('table', {'class': 'table'})
    if data_table.find('tr', {'class': 'team'}):
        return True
    else:
        return False
    

def get_all_urls(base_url: str, max_page_number: int) -> list:
    '''
    Returns BeautifulSoup objects for all pages by iterating through
    page numbers until the program reaches the last page
    '''
    urls = [f'{base_url}?page_num={num}' for num in range(1, max_page_number + 1)]
    return urls

def get_page_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_all_page_soups(urls: list[str]) -> list[BeautifulSoup]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_results = {
            executor.submit(get_page_soup, url): url for url in urls
        }
        soups = []
        for future in concurrent.futures.as_completed(future_results):
            soups.append(future.result())
        return soups

def get_specific_info(tag_object, tag_name, *possible_tag_classes) -> str:
    '''
    Returns a single piece of required info after parsing a single
    team record. Checks multiple class names in case of a possibilty
    of different class names for the same tag in the page.
    '''
    for tag_class in possible_tag_classes:
        info = tag_object.find(tag_name, {'class': tag_class})
        if info:
            return info.get_text().strip()

def get_team_info(tag_object) -> dict:
    '''
    Returns a dictionary representing one complete record in the page
    table.
    '''
    team_name = get_specific_info(tag_object, 'td', 'name')
    year = get_specific_info(tag_object, 'td', 'year')
    wins = get_specific_info(tag_object, 'td', 'wins')
    losses = get_specific_info(tag_object, 'td', 'losses')
    ot_losses = get_specific_info(tag_object, 'td', 'ot-losses')
    win_percentage = get_specific_info(
        tag_object, 'td', 'pct text-success', 'pct text-danger'
    )
    goals_for = get_specific_info(tag_object, 'td', 'gf')
    goals_against = get_specific_info(tag_object, 'td', 'ga')
    goal_difference = get_specific_info(
        tag_object, 'td', 'diff text-success', 'diff text-danger'
    )
    data = {
        'team_name': team_name,
        'year': year,
        'wins': wins,
        'losses': losses,
        'ot_losses': ot_losses,
        'win_percentage': win_percentage,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'goal_difference': goal_difference,
    }
    return data

# Used to measure the time taken by the program to execute
start_time = time.time()

BASE_URL = 'https://www.scrapethissite.com/pages/forms/'
MAX_PAGE_NUMBER = 24
urls = get_all_urls(BASE_URL, MAX_PAGE_NUMBER)

team_infos = []
teams_collected = 0

soups = get_all_page_soups(urls)

for soup in soups:
    data_table = soup.find('table', {'class': 'table'})
    teams = data_table.find_all('tr', {'class': 'team'})
    for team in teams:
        team_info = get_team_info(team)
        team_infos.append(team_info)
        teams_collected += 1
        print(teams_collected)

df = pd.DataFrame.from_dict(team_infos)
df.index = range(1, len(df) + 1)
df.index.name = 'record_id'
df.to_csv('teams.csv', index=True)

print(f'--- {time.time() - start_time} seconds ---')