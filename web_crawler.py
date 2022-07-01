import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, name, urls=[], n=100):
        self.visited_urls = []
        self.urls_to_visit = urls
        self.i = 1
        self.n = n
        self.name = name
        if not os.path.exists(f'crawler/{self.name}'):
            os.mkdir(f'crawler/{self.name}')
            os.mkdir(f'crawler/{self.name}/docs')
            os.mkdir(f'crawler/{self.name}/titles')
            self.run()

    def download_url(self, url):
        return requests.get(url).text

    def save_doc(self, title, text):
        i = self.i
        with open(f'crawler/{self.name}/docs/{i}.txt', 'w', encoding="utf-8") as d:
            d.writelines(text)
        with open(f'crawler/{self.name}/titles/{i}.txt', 'w', encoding="utf-8") as t:
            t.writelines(title)
        self.i += 1

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        title = soup.title.text
        self.save_doc(title, text)

        for link in soup.find_all('a'):
            path = link.get('href')
            if self.i > self.n:
                break
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit and self.i <= self.n:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)

if __name__ == '__main__':
    name = input('collection name > ')
    url = input('URL > ')
    n = int(input('amount of docs > '))
    Crawler(name, urls=[url], n = n)