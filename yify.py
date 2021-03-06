import re
import os
import sys
import glob
import shutil
import requests
import argparse
from unzip import unzip
from resub import Resub
from bs4 import BeautifulSoup
from decorators import ResponseTimer
from urllib.parse import urlencode, urlparse
try:
    from fuzzywuzzy import fuzz
except ImportError:
    print("install fuzzywuzzy with pip install fuzzywuzzy[speedup]")
    sys.exit()


class Yify:
    '''Api that takes a string argument from cmd line to search for subtitles'''
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('movie', type=str, action='store', help='Required argument. Searches for this given argument in yifysubtitles.com/')
        parser.add_argument('--lang', '-l', type=str, action='store', default="English", help='Language of the subtitle to search for')
        parser.add_argument('--debug', '-d', action='store_true', default=False, help='Run debug assist tools')
        parser.add_argument('--resub', '-r', action='store_true', default=False, help=Resub.__doc__)
        parser.add_argument('--no-download', '-n', dest='no', action='store_true', default=False, help='No download')
        args = parser.parse_args()
        self.movie = args.movie
        self.lang = args.lang
        self.debug = args.debug
        self.resub = args.resub
        self.no_download = args.no
        self.base_url = 'https://www.yifysubtitles.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }

        if self.debug:
            requests.get = ResponseTimer(requests.get)
        self.main()

    def main(self):
        try:
            url = self.url('search')
            payload = {'q': self.movie}
            response = requests.get(url=url, headers=self.headers, params=urlencode(payload))

            url = self.url(self.get_movie_endpoint(response))
            response = requests.get(url=url, headers=self.headers)

            subtitles = self.search_subtitle(response)
            best_rating = max([subtitle["rating"] for subtitle in subtitles])
            best_subtitles = [subtitle["endpoint"] for subtitle in subtitles if subtitle["rating"] == best_rating]

            if not self.no_download:
                self.downloader(best_subtitles[0].replace('/subtitles', 'subtitle'))
                print(f"Unzipping {self.filename}")
                unzip(self.filename)
                if self.resub:
                    Resub()

        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(e)


    def get_movie_endpoint(self, response):
        '''Parses the response of a GET@yifysubtitles.com/search?q=payload to return the endpoint page of the movie'''
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = soup.findAll("div", {"class": "media-body"})
        ratios = {}
        if movies:
            for movie in movies:
                for match in movie.findAll("a", href=True):
                    endpoint = match["href"]
                name = movie.findAll("h3", {"itemprop": "name"})[0].text
                ratio = fuzz.ratio(self.movie.lower(), name.lower())
                ratios[ratio] = {"name": name, "endpoint": endpoint}

            best_match = max(ratios.keys())
            print(f"Best match for {self.movie!r} found: {ratios[best_match]['name']}")
            return ratios[best_match]['endpoint']

        else:
            print("No movie found in search")
            sys.exit()

    def search_subtitle(self, response):
        '''Parses the response of GET@yifysubtitles.com/{movie_endpoint}.
           Returns subtitles list containing subtitle dictionaries {"rating": rating, "endpoint": endpoint}'''
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
        if subtitles:
            return subtitles

        else:
            print(f"No subtitles found for language {self.lang}")
            sys.exit

    def downloader(self, endpoint):
        '''GET@yifysubtitles.com/subtitle/{subtitle_endpoint}.zip'''
        url = self.url(endpoint + '.zip')
        with requests.get(url=url, stream=True, allow_redirects=True) as response:
            if response.ok:
                self.filename = self.get_filename(response.headers.get('content-disposition'))
                print(f"Downloading {self.filename}")
                with open(self.filename, 'wb') as zipfile:
                    shutil.copyfileobj(response.raw, zipfile)
            else:
                print(f"Request returned status code {response.status_code}")
                sys.exit()

    def get_filename(self, content_disposition):
        '''returns filename embedded in response.headers['content_disposition']'''
        if not content_disposition:
            return None
        fname = re.findall('filename=(.+)', content_disposition)
        if len(fname) == 0:
            return None
        return fname[0]

    def url(self, endpoint):
        '''Appends an endpoint to the base_url'''
        return f"{self.base_url}{endpoint}"


if __name__ == "__main__":
    app = Yify()
