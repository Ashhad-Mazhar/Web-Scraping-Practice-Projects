from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
import csv

'''
This is a simple program meant to practice scraping
tables in a web page through the use of sibling and
children tags
'''

# Open URL and create a BeautifulSoup object
html = urlopen('https://www.pythonscraping.com/pages/page3.html')
bs = BeautifulSoup(html, 'html.parser')

# Get the header row of the table so you can get its children
table_title_row = bs.find('table', {'id':'giftList'}).tr

# Create list to store all individual rows
table_rows = []

# Iterate over each row and save in the list in form of dictionaries
for sibling in table_title_row.next_siblings:
    if isinstance(sibling, Tag):
        values = sibling.find_all('td')
        table_row = {
            'Item_Title' : values[0].get_text().strip(),
            'Description' : values[1].get_text().strip(),
            'Cost' : values[2].get_text().strip().replace('$', '').replace(',', ''),
            'Image_URL' : values[3].img['src'].strip().replace('..', 'https://www.pythonscraping.com')
        }
        table_rows.append(table_row)

# Save all data to a CSV file
with open('page-3.csv', 'w') as csvFile:

    fields = ['Item_Title', 'Description', 'Cost', 'Image_URL']

    writer = csv.DictWriter(csvFile, fieldnames=fields)

    writer.writeheader()

    for row in table_rows:
        writer.writerow(row)