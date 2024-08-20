import time
from storage import DataStorage
from scraper import TransferScraper

# Dividing the code into separate modules somehow led to execution
# time being reduced from 80s to 24s while testing side by side (Why?)

def main():
    start_time = time.time()

    scraper = TransferScraper()
    records = scraper.scrape()
    storage = DataStorage()
    storage.save(records)

    print(f'--- Time taken to execute : {time.time() - start_time}s ---')


if __name__ == '__main__':
    main()