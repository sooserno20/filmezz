import requests
from multiprocessing import Pool
from multiprocessing import cpu_count
import os
from datetime import datetime
from os.path import abspath, dirname

import django
import sys

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

SITE_URL = 'http://hubmovie.cc'
MOVIES_URL = 'http://hubmovie.cc/pages/movies/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

from core.models import Movie

RETRY_FILE = open('retry.txt', 'a+', encoding='utf-8')
ERR_FILE = open('errors.txt', 'a+', encoding='utf-8')


def scrape_part(movie):
    try:
        file_name = os.path.join(dirname(dirname(abspath(__file__))), 'media', 'movie_images', str(movie.image_url).
                                 split('/')[-1])
        if os.path.exists(file_name):
            return
        response = requests.get(movie.image_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
        else:
            # write to err file movie link not processed with status_code
            RETRY_FILE.write('{}\n'.format(movie.image_url))
            ERR_FILE.write('Link {} not processed with status {}\n'.format(movie.image_url, response.status_code))
    except Exception as e:
        print(e)
        RETRY_FILE.write('{}\n'.format(movie.image_url))
        ERR_FILE.write('Link {} not processed with exc {}\n'.format(movie.image_url, str(e)))


def scrape():
    pool_size = cpu_count() * 2
    pages = list(Movie.objects.all())
    pool = Pool(pool_size)
    pool.map(func=scrape_part, iterable=pages, chunksize=int(len(pages) / pool_size))
    pool.close()
    pool.join()
    # scrape_part(Movie.objects.all()[0])
    from time import sleep
    sleep(10)


if __name__ == "__main__":
    RETRY_FILE.write(str(datetime.now()))
    ERR_FILE.write(str(datetime.now()))
    t1 = datetime.now()
    scrape()
    t2 = datetime.now()
    total = t2 - t1
    print("Image download finished in: %s" % total)
    RETRY_FILE.close()
    ERR_FILE.close()
