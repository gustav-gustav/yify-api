import re
import os
import glob
import requests
import argparse
from urllib.parse import urlencode
from bs4 import BeautifulSoup as soup


class Yify:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('string', type=str, action='store')
        parser.add_argument(
            '--debug', '-d', action='store_true', default=False)
        args = parser.parse_args()
        self.debug = args.debug
        self.movie = args.string
        self.url = 'https://www.yifysubtitles.com/search'
        self.payload = {'q': self.movie}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }
        self.res = requests.get(
            url=self.url, headers=self.headers, params=urlencode(self.payload))
        self.writer()

    def __call__(self):
        # return res
        pass

    def writer(self):
        if self.debug:
            print(self.res.url)
            # path = glob.glob(os.path.join(os.getcwd(), f"html_dump.html"))
            filename = f"html_dump.html"
            with open(filename, "wb") as f:
                f.write(self.res.content)


if __name__ == "__main__":
    app = Yify()
