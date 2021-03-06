import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from functools import reduce


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
        self.columns = list(self.selectors.keys()) + ['path']

    def get_number_of_pages(self):
        soup = self._get_page_soup(1)
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
        print(f'Requested:{url}')
        r = requests.get(url)
        _soup = BeautifulSoup(r.content, features='html.parser')
        _soup.find('div', class_=self.exceptions).decompose()
        return _soup

    def _get_page_data(self, soup):
        page_data = []
        for key in self.selectors.keys():
            content = soup.select(self.selectors[key])
            page_data.append([el.text for el in content])
        page_data.append(self.get_paths(soup))
        return list(zip(*page_data))

    @staticmethod
    def get_paths(soup):
        content = soup.find_all('a', class_="rc-DesktopSearchCard anchor-wrapper")
        return [tag.get('href') for tag in content]


# my_parser = CatalogueParser()
# print(my_parser.get_number_of_pages())


class ReviewParser:
    def __init__(self):
        self.home = 'https://www.coursera.org'

    def get_soup(self, path, tail=''):
        url = f'{self.home}{path}{tail}'
        print(f'Requested:{url}')
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='html.parser')
        return soup

    def get_skills(self, path):
        soup = self.get_soup(path)
        content = soup.select('._rsc0bd.m-r-1s.m-b-1s')
        content = [tag.get('title') for tag in content]
        return tuple(content)

    def get_estimated_time(self, path):
        soup = self.get_soup(path)
        content = soup.select('._16ni8zai.m-b-0.m-t-1s')[0]
        return content.text

    def get_language(self, path):
        soup = self.get_soup(path)
        content = soup.select('._1tu07i3a')
        content = [tag.text for tag in content]
        content = [el for el in content if el.find('Subtitles') != -1]
        if len(content) > 1:
            content = content[0]
        return content

    def get_reviews(self, path):
        content = {}

        for star in range(1, 6):
            soup = self.get_soup(path, tail=f'/reviews?sort=helpful&star={star}')
            number_of_pages = self.get_number_of_review_pages(soup)
            print(f'Star:{star} Number of Pages:{number_of_pages}')

            content[star] = []

            for page in range(1, number_of_pages + 1):
                tail = f'/reviews?sort=helpful&star={star}'
                if page > 1:
                    tail += f'&page={page}'
                    soup = self.get_soup(path, tail=tail)
                thumbs_up = self.get_review_thumbs_up(soup)
                texts = soup.select('.rc-CML.font-lg.styled')
                texts = [tag.text for tag in texts]
                content[star].extend(zip(texts, thumbs_up))
                print('Items collected:', len(content[star]))

        return content

    @staticmethod
    def get_number_of_review_pages(soup):
        content = soup.select('._b0s5mt2')
        content = [el.text for el in content]
        return int(content[-1])

    @staticmethod
    def get_review_thumbs_up(soup):
        content = soup.select('._1lutnh9y')
        content = [tag.text for tag in content]
        content = [el for el in content if el.find('Thumbs UpThis is helpful') != -1]
        return content


my_parser = ReviewParser()
my_path = '/learn/indigenous-canada'
print(my_parser.get_reviews(my_path))
