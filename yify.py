import re
import os
import glob
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
        args = parser.parse_args()
        self.debug = args.debug
        self.movie = args.movie
        self.base_url = 'https://www.yifysubtitles.com/'
        self.endpoint = 'search'
        self.url = f"{self.base_url}{self.endpoint}"
        self.payload = {'q': self.movie}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }
        if self.debug:
            requests.get = ResponseTimer(requests.get)
        self.main()

    def main(self):
        response = requests.get(
            url=self.base_url, headers=self.headers, params=urlencode(self.payload))
        # self.writer(self.res.text)
        movie_object = self.extractor(response)

        self.endpoint = movie_object['endpoint']
        self.url = f"{self.base_url}{self.endpoint}"
        response = requests.get(self.url)

    def writer(self, string):
        if self.debug:
            filename = f"html_dump.html"
            with open(filename, "w") as f:
                f.write(string)

    def extractor(self, response):
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


if __name__ == "__main__":
    app = Yify()
