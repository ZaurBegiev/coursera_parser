import requests
from bs4 import BeautifulSoup
from time import sleep
import numpy as np
from functools import reduce
import pandas as pd


class CatalogueParser:
    def __init__(self):
        self.initial_url = 'https://www.coursera.org/courses'
        self.exceptions = ['explanation-table']
        self.selectors = {
            'name': '.card-title',
            'type': '._jen3vs._1d8rgfy3',
            'source': '.partner-name.m-b-1s',
            'rating': '.ratings-text',
            'ratings': '.ratings-count',
            'students': '.enrollment-number',
            'level': '.difficulty',
        }
        self.columns = list(self.selectors.keys()) + ['link']

    def get_number_of_pages(self):
        r = requests.get(self.initial_url)
        soup = BeautifulSoup(r.content, features='html.parser')
        return int(soup.select('.box.number')[-1].text)

    def parse_page(self, page):
        soup = self._get_page_soup(page)
        print(f'Page {page} parsed...')
        return self._get_page_data(soup)

    def parse(self, threshold=np.inf):
        number_of_pages = self.get_number_of_pages()
        number_of_pages = int(min(threshold, number_of_pages))
        pages = range(1, number_of_pages+1)
        data = [self.parse_page(page) for page in pages]
        data = list(reduce(lambda prev, cur: prev + cur, data))
        data = pd.DataFrame(data, columns=self.columns)
        data.to_csv('coursera.csv', index=False)
        print('Parsing finished.')

    def _get_page_soup(self, page):
        url = f'{self.initial_url}?page={page}&index=prod_all_products_term_optimization'
        r = requests.get(url)
        _soup = BeautifulSoup(r.content, features='html.parser')
        _soup.find('div', class_=self.exceptions).decompose()
        return _soup

    def _get_page_data(self, soup):
        page_data = []
        for key in self.selectors.keys():
            content = soup.select(self.selectors[key])
            page_data.append([el.text for el in content])
        page_data.append(self._get_links(soup))
        sleep(1)
        return list(zip(*page_data))

    @staticmethod
    def _get_links(soup):
        content = soup.find_all('a', class_="rc-DesktopSearchCard anchor-wrapper")
        return [tag.get('href') for tag in content]


my_parser = CatalogueParser()
my_parser.parse(3)
