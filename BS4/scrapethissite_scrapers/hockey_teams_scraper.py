import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag

def get_specific_info(tag_object, tag_name, *possible_tag_classes) -> str:
    for tag_class in possible_tag_classes:
        info = tag_object.find(tag_name, {'class': tag_class})
        if info:
            return info.get_text().strip()

def get_team_info(tag_object) -> dict:
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


BASE_URL = 'https://www.scrapethissite.com/pages/forms/'

response = requests.get(BASE_URL, params={'page_num': 1})
html = response.content
soup = BeautifulSoup(html, 'html.parser')

data_table = soup.find('table', {'class': 'table'})
teams = data_table.find_all('tr', {'class': 'team'})

team_infos = []
teams_collected = 0

for team in teams:
    team_info = get_team_info(team)
    team_infos.append(team_info)
    teams_collected += 1
    print(teams_collected)

df = pd.DataFrame.from_dict(team_infos)
df.index = range(1, len(df) + 1)
df.index.name = 'record_id'
df.to_csv('teams.csv', index=True)