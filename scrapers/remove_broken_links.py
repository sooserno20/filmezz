import os
import sys
from os.path import abspath, dirname

import django
import requests
import urllib3
from bs4 import BeautifulSoup

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()
urllib3.disable_warnings()
from core.models import Movie, MovieLink

TIMEOUT = 5
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

HOSTS = set(MovieLink.objects.values_list('host', flat=True))
HOSTS.remove('')
print('hosts: ')
print(HOSTS)


def is_link_dead(link):
    try:
        # follow redirects (http://vidto.me/mssg5q2xm4f8.html)
        response = requests.get(link, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if 'deleted' in response.text or 'not found' in response.text:
            return True
        try:
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
            elif 'upvid.co' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('not found') != -1:
                    return True
            # SOLVE REDIRECT http://vidzi.tv/rq0qpamrtkle.html (redirects to vidzi.nu)
            # elif 'vidzi.tv' in link.link:
            #     soup = BeautifulSoup(response.text, 'lxml')
            #     if soup.h1.text.lower().index('not found') != -1:
            #         return True
            # elif 'thevideo.me' in link.link:
            #     pass
            elif 'gounlimited.to' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.select('#container')[0].text.lower().index('not found') != -1:
                    return True
            elif 'vshare.eu' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('no longer') != -1:
                    return True
            # javascript create element (hard to verify, or need selenium
            # elif 'videa.hu' in link.link:
            #     soup = BeautifulSoup(response.text, 'lxml')
            #     if soup.h1.text.lower().index('no longer') != -1:
            #         return True
            elif 'openload.co' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h6.text.lower().index('deleted') != -1:
                    return True
            elif 'vidlox.me' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('not found') != -1 or soup.h1.text.lower().index('deleted') != -1:
                    return True
            elif 'vidlox.tv' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('deleted') != -1 or soup.h1.text.lower().index('not found') != -1:
                    return True
            elif 'vidtodo.com' in link.link:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.select('#container')[0].text.lower().index('not found') != -1:
                    return True
        except Exception:
            pass
    except Exception:
        return True
    if response.status_code >= 400:
        return True
    return False


# test_links = []
# for host in HOSTS:
#     for link in MovieLink.objects.all():
#         if host.lower() in link.link:
#             print(link.link)
#             test_links.append(link.link)
#             break

# site_not_found = ['http://beta.vidup.me/3usqp60qdwlc']
# timeout = ['briskfile.com']
#
# test_links = ['http://promptfile.com/l/9A29D2D559-C86E28F9FE', 'http://vidup.me/488gitywibnm', 'http://flashx.tv/tj7l8p82uqmu.html', 'http://streamango.com/f/rfsronokstdmcbpb/1.1.2018.HDRip.XviD.AC3-EVO.avi-tt3445702-L2W.mp4', 'https://videakid.hu/player?v=SUhesWIihui450QP', 'http://vidto.me/ol5ijsn9oz06', 'http://streamin.to/oqamuq09miy7', 'http://estream.to/5sakjckpywe0.html', 'https://www.viki.com/player/1055371v', 'https://www.youtube.com/embed/JZ1MOQfCmhE', 'https://vev.io/j93wg90j8odp', 'http://estream.to/5sakjckpywe0.html', 'http://vidup.me/488gitywibnm', 'http://openload.co/f/Ye92PkVo4Go/dmd-meganleavey.2017.bdrip.x264.mkv.mp4', 'http://filez.tv/Wut', 'http://vidlox.tv/embed-jcodvfzcfj0m.html', 'http://gorillavid.in/u8w39oln4r2r', 'http://bestreams.net/8xqu3gb3od08', 'http://streamplay.to/isrxe0rwm7zd', 'http://vidto.me/ol5ijsn9oz06', 'http://flashx.tv/tj7l8p82uqmu.html']
# for l in test_links:
#     is_link_dead(l)
#
# # indavideo.hu only from hungary, remove??
# to_remove = ['allmyvideos.net', 'kingvid.tv', 'faststream.ws', 'noslocker.com']
#
# print(test_links)
# exit()
bad_count = 0
good_count = 0
for movie in Movie.objects.all():
    for link in movie.links.all():
        if is_link_dead(link):
            # link.delete()
            # if movie contains no links, delete movie
            print('BAD LINK')
            print(link)
            bad_count += 1
            print(bad_count)
        else:
            print('GOOD LINK')
            print(link)
            good_count += 1
            print(good_count)
