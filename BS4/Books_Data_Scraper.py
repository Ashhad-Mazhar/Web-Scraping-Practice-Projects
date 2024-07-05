from bs4 import BeautifulSoup
import requests
import csv

def Save_Row_To_CSV(list_of_values, mode, name_of_file):
    with open(name_of_file, mode) as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(list_of_values)

Save_Row_To_CSV(['Title', 'Price in Pounds', 'Availability Status', 'Available Books', 'Rating'], 'w', 'books.csv')

base_url = 'https://books.toscrape.com/'

source = requests.get(base_url).text

soup = BeautifulSoup(source, 'lxml')

# Indicates the source code of a single product on the main page
products = soup.find_all('article', class_ = 'product_pod')

for product in products:
    book_href = product.find('h3').a['href']

    book_url = base_url + book_href

    book_source = requests.get(book_url).text

    book_soup = BeautifulSoup(book_source, 'lxml')

    # Indicates the source code of the product details section
    product_details = book_soup.find('div', class_ = 'col-sm-6 product_main')

    book_title = product_details.find('h1').text

    # Strips the currency sign from the price after extracting it
    book_price_in_pounds = product_details.find('p', class_ = 'price_color').text.replace('Â£', '')

    book_availability = product_details.find('p', class_ = 'instock availability').text.strip()

    # Meant to extract individual values from the string of form "In Stock (22 available)"
    book_availability_status = book_availability.split('(')[0].strip()
    number_of_available_books = book_availability.split('(')[1].split()[0]

    # Returns rating in the form "One", "Two"
    # The format of the class name is "book-rating One" and so on
    # BS4 is interpreting "book-rating One" as two separate classes and returning a list of two elements
    # We need to use find_all becuase this class name varies between books having different ratings
    book_rating_string = product_details.find_all('p')[2]['class'][1]

    string_to_int = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }

    book_rating_int = string_to_int.get(book_rating_string, None)

    Save_Row_To_CSV([book_title, book_price_in_pounds, book_availability_status, number_of_available_books, book_rating_int], 'a', 'books.csv')