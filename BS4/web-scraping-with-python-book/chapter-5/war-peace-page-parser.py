from urllib.request import urlopen
from bs4 import BeautifulSoup

"""
This is a basic program meant to practice filtering tags
based on their attributes and display them separately on
the terminal
"""

html = urlopen('https://www.pythonscraping.com/pages/warandpeace.html')
bs = BeautifulSoup(html.read(), 'html.parser')

title = bs.find('h1').get_text()
print('Title:')
print(title)

chapter_name = bs.find('h2').get_text()
print('Chapter Name:')
print(chapter_name)

proper_nouns = bs.find_all('span', {'class':'green'})
print('Proper Nouns:')
for proper_noun in proper_nouns:
    print(proper_noun.get_text())

quotes= bs.find_all('span', {'class':'red'})
print('Quotes:')
for quote in quotes:
    print(quote.get_text())