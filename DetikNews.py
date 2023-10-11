import pandas as pd
from requests import get
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import datetime

class DetikNewsApi:

    def __init__(self):
        """ Search URL"""
        self.search_url = 'https://www.detik.com/search/searchall?'

    def build_search_url(self, query: str, page_number: int):
        """ Building search url with query input, we can jump to specific page number"""
        qs = f'query={query}'
        qs2 = '&siteid=2&sortby=time&sorttime=0&page='
        return self.search_url + qs + qs2 + str(page_number)

    def build_detail_url(self, url: str):
        """ Build detail URL will turn off pagination in detail page """
        a = urlsplit(url)
        qs = 'single=1'
        detail_url = a.scheme + '://' + a.netloc + a.path + '?' + qs
        return detail_url

    def result_count(self, search_response):
        """ Search result count, need search response page """
        soup = BeautifulSoup(search_response.text, 'html.parser')
        tag = soup.find('span', 'fl text').text
        count = [int(s) for s in tag.split() if s.isdigit()]
        return count[0]

    def detail(self, url: str) -> str:
        detail_url = self.build_detail_url(url)
        req = get(detail_url)
        soup = BeautifulSoup(req.text, 'html.parser')
        tag = soup.find('div', class_="detail__body-text")
        body = ''
        if tag.find_all('p'):
            for i in tag.find_all('p'):
                body += i.text
        else:
            body += tag.text
        return body

    def parse(self, search_response, detail):
        soup = BeautifulSoup(search_response.text, 'html.parser')
        tag = soup.find_all('article')
        data = []

        for i in tag:
            judul = i.find('h2').text
            link = i.find('a').get('href')
            gambar = i.find('img').get('src')
            body = ''
            if detail:
                body = self.detail(link)
            waktu = i.find('span', class_="date").text
            time_scr = datetime.date.today().strftime("%Y-%m-%d")
            data.append({'judul': judul,
                    'link': link,
                    'gambar': gambar,
                    'body': body,
                    'waktu': waktu,
                    'waktu_scraping': time_scr,
                    'berita_hoax': False
                    })
        return pd.DataFrame(data)

    def search(self, query, num_pages=1, detail=False):
        data = []

        for page_number in range(1, num_pages + 1):
            url = self.build_search_url(query, page_number)
            search_response = get(url)
            parse_result = self.parse(search_response, detail)
            data.append(parse_result)

        # Menggabungkan hasil dari semua halaman ke dalam satu DataFrame
        if data:
            combined_data = pd.concat(data, ignore_index=True)
            return combined_data
        else:
            return pd.DataFrame()
