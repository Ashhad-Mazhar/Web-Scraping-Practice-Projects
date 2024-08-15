import json
import requests
import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def get_page_json(url: str):
    response = requests.get(url)
    return response.content

def get_all_pages_jsons(urls: list[str]) -> list[str]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_results = {
            executor.submit(get_page_json, url): url for url in urls
        }
        json_records = []
        for future in concurrent.futures.as_completed(future_results):
            json_records.append(future.result())
    return json_records


URLS = [
    f'https://www.scrapethissite.com/pages/ajax-javascript/?ajax=true&year={year}'
    for year in range(2010, 2015 + 1)
]

records = []
json_files = get_all_pages_jsons(URLS)

for json_file in json_files:
    page_records = json.loads(json_file)
    for record in page_records:
        if record.get('best_picture', -1) == -1:
            record['best_picture'] = False
        records.append(record)
    

df = pd.DataFrame.from_dict(records)
df.index = range(1, len(df) + 1)
df.index.name = 'row_number'
df.to_csv('films.csv', index=True)