import os
import urllib.request
from datetime import datetime
from os.path import abspath, dirname

import requests
import urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm
import django
import sys

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()
urllib3.disable_warnings()
from core.models import Movie, MovieLink

TIMEOUT = 5
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

HOSTS = set(MovieLink.objects.values_list('host'))
print('hosts: ')
print(HOSTS)


def is_link_dead(link):
    try:
        # follow redirects (http://vidto.me/mssg5q2xm4f8.html)
        response = requests.get(link, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if 'vidoza' in link.link:
            soup = BeautifulSoup(response.text, 'lxml')
            # file size 0.0 mb
            if soup.h2.span.text.index('0.0') != -1:
                return True
        elif 'vev.io' in link.link:
            soup = BeautifulSoup(response.text, 'lxml')
            if soup.title.text.lower().index('not found') != -1:
                return True
        elif 'flashx.co' in link.link:
            soup = BeautifulSoup(response.text, 'lxml')
            if soup.select('#main b')[0].text.lower().index('not found') != -1:
                return True
        else:
            pass
    except Exception:
        return True
    if response.status_code >= 400:
        return True
    return False


for movie in Movie.objects.all():
    for link in movie.links.all():
        if is_link_dead(link):
            # link.delete()
            print('BAD LINK')
            print(link)
        else:
            print('GOOD LINK')
            print(link)
