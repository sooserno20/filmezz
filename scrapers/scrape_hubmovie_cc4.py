import ctypes
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from sys import exit

from django.utils.text import slugify
from requests.exceptions import Timeout
import requests
from bs4 import BeautifulSoup
from multiprocessing import cpu_count, Lock, Pool, Value
from os.path import exists
from datetime import datetime
from os.path import abspath, dirname

import django
import sys

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

import json
from core.models import Movie


SITE_URL = 'http://hubmovie.cc'
MOVIES_URL = 'http://hubmovie.cc/pages/movies/'
SERIES_URL = 'http://hubmovie.cc/pages/shows/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
RETRY_FILE = open('retry.txt', 'a+', encoding='utf-8')
ERR_FILE = open('errors.txt', 'a+', encoding='utf-8')

def strip_nbsp(title):
    if title.endswith('nbsp'):
        return title[:-4]
    return title

try:
    with open('movies_crawled_hubmovie.txt', 'r', encoding='utf-8') as f:
        MOVIES_ALREADY_CRAWLED = f.read().split('\n')
        NORMALIZED_MOVIES_ALREADY_CRAWLED = [strip_nbsp(m) for m in MOVIES_ALREADY_CRAWLED]
except IOError:
    MOVIES_ALREADY_CRAWLED = []
    NORMALIZED_MOVIES_ALREADY_CRAWLED = []

MOVIES_CRAWLED = open('movies_crawled_hubmovie.txt', 'a+', encoding='utf-8')
t1 = datetime.now()
is_estimated_time_calculated = Value(ctypes.c_bool, False)
lock = Lock()
# MOVIES_ALREADY_CRAWLED2 = [list(m.keys())[0] for m in MOVIES_ALREADY_CRAWLED]


def scrape_movie_part(page):
    global is_estimated_time_calculated
    result = {}
    try:
        response = requests.get('{}{}'.format(MOVIES_URL, page), headers=HEADERS, timeout=10)
    except Exception as e:
        print(e)
        print(page)
        return result
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        links = [link.get('href') for link in soup.find(id='movies_cont').find_all('a')
                 if link.get('href') not in MOVIES_ALREADY_CRAWLED]
        links_tmp = []
        # for link in links:
        #     for slug in movies_in_db:
        #         link_slug = link.split('/')[-1]
        #         if SequenceMatcher(a=link_slug, b=slug).ratio() > 0.9:
        #             links_tmp.append(link)
        # links = links_tmp
        # links = [link for link in links if link.split('/')[-1] not in movies_in_db]
        timeouts = 0
        for link in links:
            try:
                if link.startswith('.'):
                    link = '{}{}'.format(SITE_URL, link[1:])
                response = requests.get(link, headers=HEADERS, timeout=10)
                # if request was successful reset the timeouts counter
                timeouts = 0
                if response.status_code == 200:
                    soup_detail = BeautifulSoup(response.text, 'lxml')
                    name = soup_detail.find(itemprop="name").text
                    movie_links = soup_detail.select('.link_row')
                    if not movie_links:
                        continue

                    result[name] = {'links': [{'link': str(movie_link.find('a').get('href').encode("utf-8")),
                                               'host': str(movie_link.find(class_='link_host').text)} for movie_link in movie_links],
                                    'description': soup_detail.find(id='desc').text if soup_detail.find(id='desc') else ''}
                    details = soup_detail.find(id='stats_cont')
                    genres = []
                    for genre_a in details.find_all(class_='text')[0].find_all('a'):
                        genres.append(genre_a.text)
                    result[name]['genres'] = genres
                    result[name]['year'] = details.find_all(class_='text')[1].find('a').text \
                        if details.find_all(class_='text')[1].find('a') else ''
                    directors = []
                    for d_a in details.find_all(class_='text')[3].find_all('a'):
                        if d_a:
                            directors.append(d_a.text)
                    result[name]['directors'] = directors
                    actors = []
                    for actor_a in details.find_all(class_='text')[4].find_all('a'):
                        if actor_a:
                            actors.append(actor_a.text)
                    result[name]['actors'] = actors
                    result[name]['imdb_score'] = soup_detail.find(id='score').text if soup_detail.find(id='score') else 0
                    result[name]['image_path'] = soup_detail.find(class_='poster ').get('src') if soup_detail.find(class_='poster ') else ''
                    with lock:
                        link = link.replace(SITE_URL, '.')
                        MOVIES_CRAWLED.write(link + '\n')
                        MOVIES_CRAWLED.flush()
            except Exception as e:
                print(e)
                if isinstance(e, Timeout):
                    timeouts += 1
                    if timeouts == 3:
                        # third time continous timeout, seems that the site isn't up, so exit
                        print('Site is down, exiting..')
                        exit()
                with lock:
                    RETRY_FILE.write('{}\n'.format(page))
                    RETRY_FILE.flush()
                    ERR_FILE.write('Link {} not processed with exc {}\n'.format(link, str(e)))
                    ERR_FILE.flush()

        if not is_estimated_time_calculated.value:
            # TODO: on fucking windows the lock mechanism doesn't work
            with lock:
                is_estimated_time_calculated.value = True
                t2 = datetime.now()
                time_taken = t2 - t1
                est_time = time_taken * (calculate_last_movie_page() - cpu_count()) / cpu_count()
                print('Time estimated: {}'.format(est_time))
    else:
        print('Status {}'.format(response.status_code))
    return result


def scrape_series_part(page):
    global is_estimated_time_calculated
    result = {}
    response = requests.get('{}{}'.format(SERIES_URL, page), headers=HEADERS, timeout=10)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        links = [link.get('href') for link in soup.find(id='movies_cont').find_all('a')]
                 # if link.get('href') not in MOVIES_ALREADY_CRAWLED]
        timeouts = 0
        for link in links:
            try:
                if link.startswith('.'):
                    link = '{}{}'.format(SITE_URL, link[1:])
                response = requests.get(link, headers=HEADERS, timeout=10)
                # if request was successful reset the timeouts counter
                timeouts = 0
                if response.status_code == 200:
                    soup_detail = BeautifulSoup(response.text, 'lxml')
                    name = soup_detail.h2.text
                    result[name] = {}
                    details = soup_detail.find(id='stats_cont')
                    genres = []
                    for genre_a in details.find_all(class_='text')[0].find_all('a'):
                        genres.append(genre_a.text)
                    result[name]['genres'] = genres
                    result[name]['year'] = details.find_all(class_='text')[1].find('a').text \
                        if details.find_all(class_='text')[1].find('a') else ''
                    directors = []
                    for d_a in details.find_all(class_='text')[3].find_all('a'):
                        if d_a:
                            directors.append(d_a.text)
                    result[name]['directors'] = directors
                    actors = []
                    for actor_a in details.find_all(class_='text')[4].find_all('a'):
                        if actor_a:
                            actors.append(actor_a.text)
                    result[name]['actors'] = actors
                    result[name]['imdb_score'] = soup_detail.find(id='score').text if soup_detail.find(
                        id='score') else 0
                    result[name]['image_path'] = soup_detail.find(class_='poster ').get('src') if soup_detail.find(
                        class_='poster ') else ''
                    result[name]['is_series'] = True

                    epi_links = ['{}{}'.format(SITE_URL, epi_link.a.get('href')) for epi_link in soup_detail.find_all(class_='link_go')]
                    for epi_link in epi_links:
                        try:
                            response = requests.get(epi_link, headers=HEADERS, timeout=10)
                            if response.status_code == 200:
                                soup_detail = BeautifulSoup(response.text, 'lxml')
                                movie_links = soup_detail.select('.link_row')
                                if not movie_links:
                                    continue
                                try:
                                    season = epi_link.split('/')[-1].split('-')[1]
                                    episode = epi_link.split('/')[-1].split('-')[3]
                                except Exception as e:
                                    print(e)
                                    print(epi_link)
                                    continue
                                result[name].setdefault(season, {})
                                result[name][season][episode] = {'links': [{'link': str(movie_link.find('a').get('href').encode("utf-8")),
                                                                 'host': str(movie_link.find(class_='link_host').text)} for movie_link in movie_links],
                                                                 'description': soup_detail.find(id='desc').text if soup_detail.find(id='desc') else ''}
                            else:
                                print(epi_link)
                                print(response.status_code)
                        except Exception as e:
                            print(epi_link)
                            print(e)
                else:
                    # write to err file movie link not processed with status_code
                    with lock:
                        RETRY_FILE.write('{}\n'.format(page))
                        RETRY_FILE.flush()
                        ERR_FILE.write('Link {} not processed with status {}\n'.format(link, response.status_code))
                        ERR_FILE.flush()
            except Exception as e:
                print(e)
                if isinstance(e, Timeout):
                    timeouts += 1
                    if timeouts == 3:
                        # third time continuous timeout, seems that the site isn't up, so exit
                        print('Site is down, exiting..')
                        exit()
                with lock:
                    RETRY_FILE.write('{}\n'.format(page))
                    RETRY_FILE.flush()
                    ERR_FILE.write('Link {} not processed with exc {}\n'.format(link, str(e)))
                    ERR_FILE.flush()

        if not is_estimated_time_calculated.value:
            # TODO: on fucking windows the lock mechanism doesn't work
            with lock:
                is_estimated_time_calculated.value = True
                t2 = datetime.now()
                time_taken = t2 - t1
                est_time = time_taken * (calculate_last_movie_page() - cpu_count()) / cpu_count()
                print('Time estimated: {}'.format(est_time))

        return result

    else:
        print('Status {}'.format(response.status_code))


def scrape_movies():
    pool_size = cpu_count() * 8
    pool_size = 8
    pages = list(range(1, calculate_last_movie_page()))
    # pages = list(range(1, 4))
    pool = Pool(pool_size)
    # for debugging comment out this
    data = pool.map(func=scrape_movie_part, iterable=pages, chunksize=int(len(pages) / pool_size))
    pool.close()
    pool.join()
    # for debugging
    # scrape_movie_part(10)
    return data


def scrape_series():
    # TODO: save series on the go, not just at the finish
    pool_size = min(cpu_count() * 8, calculate_last_series_page() - 1)
    pool_size = 2  # seems to be a max connection set at hubmovies.cc (508 errors)
    # pool_size = 2
    pages = list(range(1, calculate_last_series_page()))
    # pages = list(range(1, 3))
    pool = Pool(pool_size)
    # for debugging comment out this
    data = pool.map(func=scrape_series_part, iterable=pages, chunksize=int(len(pages) / pool_size))
    pool.close()
    pool.join()
    # for debugging
    # scrape_series_part(1)
    return data


def calculate_last_movie_page():
    """Calculate last page with binary search"""
    # TODO: implement logic
    # last_page = 1000
    # response = requests.get(START_URL + str(last_page))
    # soup = BeautifulSoup(response.text, 'lxml')
    # links = soup.select('#movies_cont > a')
    # while not links:
    return 417


def calculate_last_series_page():
    """Calculate last page with binary search"""
    return 64


if __name__ == "__main__":
    # if exists('retry.txt'):
    #     with open('retry.txt', 'r', encoding='utf-8') as retry_file:
    #         pages = set()
    #         for page in retry_file:
    #             try:
    #                 pages.add(int(page))
    #             except ValueError:
    #                 pass
    #     # delete last character ,]
    #     with open('hubmovie_cc2.json', 'rb+') as retry_file:
    #         retry_file.seek(-2, os.SEEK_END)
    #         retry_file.truncate()
    #     with open('hubmovie_cc2.json', 'a+', encoding='utf-8') as f:
    #         f.write(',\n')
    #     pages = list(pages)
    #     with open('hubmovie_cc2.json', 'a+', encoding='utf-8') as f:
    #         for page in pages:
    #             # TODO: rewrite to work on specific links, not on whole pages
    #             scraped_data = scrape_movie_part(int(page))
    #             json.dump(scraped_data, f)
    #             if page != pages[-1]:
    #                 f.write(',')
    #             f.write('\n')
    #         f.write(']')
    #     os.remove('retry.txt')
    #     exit()
    # movies_in_db = Movie.objects.filter(is_series=False).values_list('title', flat=True)
    # movies_in_db = [slugify(title) for title in movies_in_db]

    data = scrape_movies()
    if data:
        with open('hubmovie_cc5.json', 'a+', encoding='utf-8') as f:
            f.write('[\n')
            for entry in data:
                json.dump(entry, f)
                # if entry != data[-1]:
                #     f.write(',')
                f.write(',\n')
                # f.write('\n')
            # f.write(']')
            t2 = datetime.now()
            total = t2 - t1
            print("Scraping finished in: %s" % (total))
    # print('NO SERIES')
    # sys.exit(0)

    # series_in_db = Movie.objects.filter(is_series=True).values_list('title', flat=True)
    # temp = []
    # for title in series_in_db:
    #     try:
    #         temp.append(title[:title.index('season')].strip())
    #     except ValueError:
    #         temp.append(title.strip())
    # series_in_db = temp
    # series_in_db = [slugify(title) for title in series_in_db]
    data = scrape_series()
    if data:
        with open('hubmovie_cc5.json', 'a+', encoding='utf-8') as f:
            # f.write('[\n')
            for entry in data:
                json.dump(entry, f)
                if entry != data[-1]:
                    f.write(',')
                f.write('\n')
            f.write(']')
            t2 = datetime.now()
            total = t2 - t1
            print("Scraping finished in: %s" % (total))
    RETRY_FILE.close()
    ERR_FILE.close()
