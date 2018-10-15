import urllib3
from PIL import Image
import pytesseract
import io
import ctypes
import json
import urllib.parse
from datetime import datetime
from multiprocessing import cpu_count, Lock, Pool, Value
from sys import exit

import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout
urllib3.disable_warnings()

TIMEOUT = 20
SITE_URL = 'http://filmezz.eu/'
MOVIES_URL = 'http://filmezz.eu/kereses.php'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

with open('movies_crawled.txt', 'r', encoding='utf-8') as f:
    MOVIES_ALREADY_CRAWLED = f.read().split('\n')

RETRY_FILE = open('retry.txt', 'a+', encoding='utf-8')
ERR_FILE = open('errors.txt', 'a+', encoding='utf-8')
OUTPUT_FILE = open('filmezz_eu4.json', 'a+', encoding='utf-8')
MOVIES_CRAWLED = open('movies_crawled.txt', 'a+', encoding='utf-8')
t1 = datetime.now()
is_estimated_time_calculated = Value(ctypes.c_bool, False)
lock = Lock()


def scrape_part(page):
    global is_estimated_time_calculated
    result = {}
    response = requests.get('{}?p={}'.format(MOVIES_URL, page, headers=HEADERS, timeout=TIMEOUT))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        links = [link.get('href') for link in soup.find(class_='movie-list').find_all('a')
                 if link.get('href') not in MOVIES_ALREADY_CRAWLED]
        timeouts = 0
        for link in links:
            try:
                link_part = link
                link = '{}{}'.format(SITE_URL, link)
                response = requests.get(link, headers=HEADERS, timeout=TIMEOUT)
                # if request was successful reset the timeouts counter
                timeouts = 0
                if response.status_code != 200:
                    continue
                soup_detail = BeautifulSoup(response.text, 'lxml')
                name_and_year = soup_detail.find('h1').text.strip()
                english_name = soup_detail.find('h2').text.strip()
                if name_and_year[-1] == ')':
                    name = name_and_year[:-6]
                    year = name_and_year[-5:-1]
                else:
                    name = name_and_year
                    year = 0
                movie_links = soup_detail.find(class_='content-box').find(class_='url-list').\
                                  find_all('li', recursive=False)[1:]
                if not movie_links:
                    continue

                result[name] = {
                    'links': [{'link': str(movie_link.find('a').get('href').split('/')[-1]),
                               'info': str(movie_link.find(class_='col-sm-4 col-xs-12').text.strip()),
                               'host': str(movie_link.div.text.strip()),
                               'language': str(movie_link.div.ul.li.get('title'))} for movie_link in movie_links],
                    'description': soup_detail.find('div', class_='text').text.strip()
                                        if soup_detail.find('div', class_='text') else ''}
                result[name]['is_series'] = 'epi' in \
                                            movie_links[0].find(class_='col-sm-4 col-xs-12').text  # epizod, episode
                result[name]['english_name'] = english_name
                result[name]['year'] = year
                genres = []
                for genre_a in soup_detail.find(class_='category').find_all('a'):
                    genres.append(genre_a.text)
                result[name]['genres'] = genres

                details = soup_detail.find('aside', class_='sidebar').find_all('ul')[1:]
                directors = []
                for d_a in details[0].find_all('a'):
                    if d_a:
                        directors.append(d_a.text)
                result[name]['directors'] = directors
                actors = []
                for actor_a in details[1].find_all('a'):
                    if actor_a:
                        actors.append(actor_a.text)
                result[name]['actors'] = actors
                result[name]['imdb_score'] = soup_detail.find(class_='score').text if soup_detail.find(
                    class_='score') else 0
                result[name]['image_path'] = soup_detail.find('img').get('src')
                print(name)
                timeo = False
                for linkk in result[name]['links'][:]:
                    try:
                        linkk['link'] = urllib.parse.unquote(linkk['link'])
                        session = requests.session()
                        try:
                            resp = session.get(linkk['link'], timeout=TIMEOUT, verify=False)
                        except Timeout as e:
                            if 'filmezz' not in e.args[0].pool.host:
                                result[name]['links'].remove(linkk)
                                continue
                            timeo = True
                            break
                        # no captcha
                        if 'filmezz' not in resp.url:
                            linkk['link'] = resp.url
                            continue
                        try:
                            resp = session.get('http://filmezz.eu/captchaimg.php', headers=HEADERS,
                                               timeout=TIMEOUT, verify=False)
                        except Timeout:
                            timeo = True
                            break
                        im = Image.open(io.BytesIO(resp.content))
                        text = pytesseract.image_to_string(im, lang='eng', config='--psm 7')
                        text = text.strip().replace(':', '').replace('O', '0').replace('=', '').strip()
                        form_data = {'captcha': eval(text)}
                        resp = session.post(linkk['link'], data=form_data)
                        linkk['link'] = resp.url
                    except Exception:
                        print('EXCCCCC' + str(name) + str(linkk) + str(timeo))
                        result[name]['links'].remove(linkk)
                if timeo:
                    continue
                with lock:
                    # !!!!!!!! remember link, not name
                    json.dump({name: result[name]}, OUTPUT_FILE)
                    OUTPUT_FILE.write(',\n')
                    OUTPUT_FILE.flush()
                    MOVIES_CRAWLED.write(link_part + '\n')
                    MOVIES_CRAWLED.flush()
            except Exception as e:
                print(e)
                if isinstance(e, Timeout):
                    timeouts += 1
                    if timeouts == 3:
                        # third time continous timeout, seems that the site isn't up, so exit
                        print('Site is down, exiting..')
                        exit()
                else:
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
                est_time = time_taken * (calculate_last_page() - cpu_count()) / cpu_count()
                print('Time estimated: {}'.format(est_time))

        return result

    else:
        print('Status {}'.format(response.status_code))


def scrape():
    pool_size = cpu_count() * 8
    pages = list(range(1, calculate_last_page()))
    pool = Pool(pool_size)
    # for debugging comment out this
    pool.map(func=scrape_part, iterable=pages, chunksize=int(len(pages) / pool_size))
    pool.close()
    pool.join()
    # for debugging
    # scrape_part(1)


def calculate_last_page():
    """Calculate last page with binary search"""
    # TODO: implement logic
    # last_page = 1000
    # response = requests.get(START_URL + str(last_page))
    # soup = BeautifulSoup(response.text, 'lxml')
    # links = soup.select('#movies_cont > a')
    # while not links:
    return 605


if __name__ == "__main__":
    scrape()
    t2 = datetime.now()
    total = t2 - t1
    print("Scraping finished in: %s" % (total))

    RETRY_FILE.close()
    ERR_FILE.close()
    OUTPUT_FILE.close()
    MOVIES_CRAWLED.close()
