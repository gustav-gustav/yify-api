import re
import os
import glob
import shutil
import requests
import argparse
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from decorators import ResponseTimer


class Yify:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('movie', type=str, action='store')
        parser.add_argument(
            '--debug', '-d', action='store_true', default=False)
        parser.add_argument('--write', '-w', action='store_true', default=False)
        parser.add_argument('--lang', '-l', action='store', default="English")
        args = parser.parse_args()
        self.movie = args.movie
        self.lang = args.lang
        self.debug = args.debug
        self.write = args.write
        self.base_url = 'https://www.yifysubtitles.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }
        if self.debug:
            requests.get = ResponseTimer(requests.get)
        self.main()

    def main(self):
        url = self.url('search')
        payload = {'q': self.movie}

        response = requests.get(
            url=url, headers=self.headers, params=urlencode(payload))

        url = self.url(self.api1(response)['endpoint'])
        response = requests.get(url=url, headers=self.headers)
        subtitles = self.api2(response)
        # print(subtitles)
        best_rating = max([subtitle["rating"] for subtitle in subtitles])
        best_subtitles = [subtitle["endpoint"] for subtitle in subtitles if subtitle["rating"] == best_rating]

        self.downloader(best_subtitles[0].replace('/subtitles', 'subtitle'))

    def writer(self, string):
        if self.debug:
            filename = f"html_dump.html"
            with open(filename, "w") as f:
                print(f"writing to {filename}")
                f.write(string)

    def api1(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = soup.findAll("div", {"class": "media-body"})
        ratios = {}
        if movies:
            for movie in movies:
                for match in movie.findAll("a", href=True):
                    endpoint = match["href"]
                name_tag = movie.findAll("h3", {"itemprop": "name"})
                name = name_tag[0].text
                ratio = fuzz.ratio(self.movie.lower(), name.lower())
                ratios[ratio] = {"name": name, "endpoint": endpoint}

            best_match = max(ratios.keys())
            print(f"best match for {self.movie!r} found: {ratios[best_match]['name']}")
            return ratios[best_match]

        else:
            print("no movie found")

    def api2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = soup.findAll("tbody")[0].findAll("tr")
        subtitles = []
        for movie in movies:
            tds = movie.findAll("td")
            #getting language index 1
            flag_cell = tds[1]
            language = flag_cell.findAll("span", {"class": "sub-lang"})[0].text
            if language == self.lang:
                #getting rating index 0
                rating_cell = tds[0]
                span = rating_cell.findAll("span", {"class": "label label-success"})
                if span:
                    rating = int(span[0].text)
                else:
                    rating = 0
                #getting endpoint index 5
                download_cell = tds[5].findAll("a", {"class": "subtitle-download"})
                endpoint = download_cell[0]["href"]
                #subtitles dictionary
                subtitle = {'rating': rating, 'endpoint': endpoint}
                subtitles.append(subtitle)

        return subtitles

    def downloader(self, endpoint):
        url = self.url(endpoint + '.zip')
        with requests.get(url=url, stream=True, allow_redirects=True) as response:
            filename = self.get_filename(response.headers.get('content-disposition'))
            with open(filename, 'wb') as zipfile:
                shutil.copyfileobj(response.raw, zipfile)

    def get_filename(self, content_disposition):
        """
        Get filename from content-disposition
        """
        if not content_disposition:
            return None
        fname = re.findall('filename=(.+)', content_disposition)
        if len(fname) == 0:
            return None
        return fname[0]

    def url(self, endpoint):
        return f"{self.base_url}{endpoint}"


if __name__ == "__main__":
    app = Yify()
