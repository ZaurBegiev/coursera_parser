import requests
from bs4 import BeautifulSoup
from time import sleep
import numpy as np
from functools import reduce
import pandas as pd


class Parser:
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
        def get_page_soup(_parser, _page):
            url = f'{_parser.initial_url}?page={_page}&index=prod_all_products_term_optimization'
            r = requests.get(url)
            _soup = BeautifulSoup(r.content, features='html.parser')
            _soup.find('div', class_=_parser.exceptions).decompose()
            return _soup

        def get_page_data(_parser, _soup):
            page_data = []
            for key in _parser.selectors.keys():
                content = soup.select(_parser.selectors[key])
                page_data.append([el.text for el in content])
            page_data.append(get_links(_soup))
            sleep(1)
            return list(zip(*page_data))

        def get_links(_soup):
            content = _soup.find_all('a', class_="rc-DesktopSearchCard anchor-wrapper")
            return [tag.get('href') for tag in content]

        soup = get_page_soup(self, page)
        print(f'Page {page} parsed...')
        return get_page_data(self, soup)

    def parse(self, threshold=np.inf):
        number_of_pages = self.get_number_of_pages()
        number_of_pages = int(min(threshold, number_of_pages))
        pages = range(1, number_of_pages+1)
        data = [self.parse_page(page) for page in pages]
        data = list(reduce(lambda prev, cur: prev + cur, data))
        data = pd.DataFrame(data, columns=self.columns)
        data.to_csv('coursera.csv', index=False)
        print('Parsing finished.')


parser = Parser()
parser.parse(3)
