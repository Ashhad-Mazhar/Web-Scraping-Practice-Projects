import time
import asyncio
from storage import DataStorage
from scraper import TransferScraper

async def main():
    start_time = time.time()

    scraper = TransferScraper()
    records = await scraper.scrape()
    storage = DataStorage()
    storage.save(records)

    print(f'--- Time taken to execute : {time.time() - start_time}s ---')


if __name__ == '__main__':
    asyncio.run(main())