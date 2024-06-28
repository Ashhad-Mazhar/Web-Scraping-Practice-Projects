from bs4 import BeautifulSoup
import requests
import csv

with open('books.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Title', 'Price in Pounds', 'Availability'])

    source = requests.get('https://books.toscrape.com/').text

    soup = BeautifulSoup(source, 'lxml')

    products = soup.find_all('article', class_='product_pod')

    for product in products:
        title = product.h3.a['title']

        price = product.find('div', class_='product_price').find('p', class_='price_color').text.replace('Â£', '')

        availability = product.find('div', class_='product_price').find('p', class_='instock availability').text.strip()

        csv_writer.writerow([title, price, availability])