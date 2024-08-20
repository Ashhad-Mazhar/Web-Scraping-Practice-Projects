import re
import os
import time
import config
import requests
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from scraper import TransferScraper
from concurrent.futures import ThreadPoolExecutor

def main():
    start_time = time.time()

    scraper = TransferScraper()
    transfer_records = scraper.scrape()
    store_data(transfer_records, config.CSV_FILENAME, config.IMAGES_PATH)

    print(f'--- Time to execute : {time.time() - start_time}s ---')

def get_image_filename(image_url: str, player_name: str) -> str:
    '''
    Returns the filename that should be used for the image.
    Filename is determined by concatenating players name and
    the file extension extracted with re from the given URL
    '''
    regex = re.compile(r'(\.[a-zA-Z]{3,4})(?=\?lm=1)')
    match = regex.search(image_url)
    if match:
        file_extension = match[1].lower()
        filename = player_name + file_extension
        return filename
    else:
        print(f"There was an error while finding {player_name} image's filename")
        return f'{player_name}_unknown_extension.jpg'

def download_images(records: list[dict]) -> None:
    '''
    Scrapes the images for each player in the provided list of
    records and then appends them in-place to each of the dictionary
    '''
    scraper = TransferScraper()
    for record in records:
        image_data = scraper.fetch_url(record['player_image_url'])
        record['player_image'] = {
            'data': image_data,
            'filename': get_image_filename(
                record['player_image_url'], record['player_name']
            )
        }

def store_images(records: list[dict], dir_name: str) -> bool:
    '''
    Stores images according to player names in the specified directory
    name in the current path
    '''
    try:
        dir_path = os.path.join(os.path.curdir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        download_images(records)
        for record in records:
            image_data = record['player_image']['data']
            image_filename = record['player_image']['filename']
            try:
                with open(os.path.join(dir_path, image_filename), 'wb') as file:
                    file.write(image_data)
            except:
                print(f'Error while writing to image file: {image_filename}')
        return True
    except:
        return False

def store_in_csv(records: list[dict], filepath: str) -> bool:
    '''
    Applies some transformations to the given list of records, sorts
    it according to the transfer fee and then stores it in a csv file
    '''
    try:
        df = pd.DataFrame.from_dict(records)
        # Dropping images as they have already been written on disk
        df.drop(columns=['player_image'], inplace=True)
        # Transforming values like "€100.23m" into "100230000"
        df['player_value_in_euros'] = (df['player_value_in_euros']
                .str.replace('€', '')
                .str.replace('.', '')
                .str.replace('m', '0000')
        )
        df['transfer_fee_in_euros'] = (df['transfer_fee_in_euros']
                .str.replace('€', '')
                .str.replace('.', '')
                .str.replace('m', '0000')
        )
        # Converting transfer fees to numeric so sorting
        # is done correctly
        df['transfer_fee_in_euros'] = pd.to_numeric(
            df['transfer_fee_in_euros'], errors='coerce'
        )
        df.sort_values('transfer_fee_in_euros', ascending=False, inplace=True)
        df.index = range(1, len(df) + 1)
        df.index.name = 'transfer_id'

        df.to_csv(filepath, index=True)
        return True
    except:
        return False
    
def store_data(records: list[dict], csv_filename: str, images_dir_name: str):
    if store_images(records, images_dir_name):
        print('Images have been written to disk')
    else:
        print('There was an error while writing images to disk')
    if store_in_csv(records, csv_filename):
        print('Data has been written to csv')
    else:
        print('There was an error while writing data to csv')


if __name__ == '__main__':
    main()