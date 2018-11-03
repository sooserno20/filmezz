
# !!!! TO RUN SCRIPT FIRST SET ALL MOVIELINKS to MovieLinks.objects.update(verified=False)
import os
import sys
from datetime import datetime
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from multiprocessing import Process
from os.path import abspath, dirname

import django
import requests
import urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()
urllib3.disable_warnings()
from core.models import Movie, MovieLink

TIMEOUT = 10
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

HOSTS = set(MovieLink.objects.values_list('host', flat=True))
print('hosts: ')
print(HOSTS)
print(len(HOSTS))


def is_link_dead(link):
    try:
        # follow redirects (http://vidto.me/mssg5q2xm4f8.html, http://gorillavid.in/u8w39oln4r2r)
        response = requests.get(link[1], headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if 'deleted' in response.text or 'not found' in response.text or 'not available' in response.text:
            return True
        try:
            if 'vidoza' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                # file size 0.0 mb
                if soup.h2.span.text.index('0.0') != -1:
                    return True
            elif 'vev.io' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.title.text.lower().index('not found') != -1:
                    return True
            elif 'flashx' in link[1] or 'flashx' in response.url:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.select('#main b')[0].text.lower().index('not found') != -1:
                    return True
            elif 'upvid.co' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('not found') != -1:
                    return True
            # SOLVE REDIRECT http://vidzi.tv/rq0qpamrtkle.html (redirects to vidzi.nu)
            # elif 'vidzi.tv' in link[1]:
            #     soup = BeautifulSoup(response.text, 'lxml')
            #     if soup.h1.text.lower().index('not found') != -1:
            #         return True
            # elif 'thevideo.me' in link[1]:
            #     pass
            elif 'gounlimited.to' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.select('#container')[0].text.lower().index('not found') != -1:
                    return True
            elif 'vshare.eu' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('no longer') != -1:
                    return True
            # javascript create element (hard to verify, or need selenium
            # elif 'videa.hu' in link[1] or 'videakid.hu' in link[1]:
            #     soup = BeautifulSoup(response.text, 'lxml')
            #     if soup.h1.text.lower().index('parameter hiba') != -1:
            #         return True
            elif 'openload.co' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h6.text.lower().index('deleted') != -1:
                    return True
            elif 'vidlox.me' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('not found') != -1 or soup.h1.text.lower().index('deleted') != -1:
                    return True
            elif 'vidlox.tv' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.h1.text.lower().index('deleted') != -1 or soup.h1.text.lower().index('not found') != -1:
                    return True
            elif 'vidtodo.com' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup.select('#container')[0].text.lower().index('not found') != -1:
                    return True
            elif 'viki.com' in link[1]:
                soup = BeautifulSoup(response.text, 'lxml')
                if soup(class_='video-error-message')[0].text.lower().index('unavailable') != -1:
                    return True
        except Exception:
            pass
    except Exception:
        return True
    if 400 <= response.status_code < 500:
        # VERIFY if this is the case with other hosts too
        # if 'openload.co' in link[1]:
        #     return False
        return True
    return False

# test_links = []
# for host in HOSTS:
#     for link in MovieLink.objects.all():
#         if host.lower() in link.link:
#             print(link.link)
#             test_links.append(link.link)
#             break

# site_not_found = ['http://beta.vidup.me/3usqp60qdwlc', 'http://www.streamin.to']
# timeout = ['briskfile.com', 'http://promptfile.com']
# hard_to_solve = ['https://www.youtube.com']
#
# test_links = []
# for l in test_links:
#     is_link_dead(('id', l))
#
# # indavideo.hu only from hungary, remove??
# to_remove = ['allmyvideos.net', 'kingvid.tv', 'faststream.ws', 'noslocker.com', 'filez.tv', 'bestreams.net']
#
# print(test_links)
# exit()


def tmp(links):
    for link in links:
        m = MovieLink.objects.get(id=link[0])
        if is_link_dead(link):
            m.delete()
        else:
            m.verified = True
            m.save()


grouped_links = {}
for host in HOSTS:
    grouped_links[host] = []
for host in HOSTS:
    for link in MovieLink.objects.filter(verified=False).values_list('id', 'host', 'link'):
        if host == link[1]:
            grouped_links[host].append((link[0], link[2]))

# print(sum(len(grouped_links[g]) for g in grouped_links))

processes = []
for key, value in grouped_links.items():
    processes.append(Process(target=tmp, args=(value, )))

for process in processes:
    process.start()

for process in processes:
    process.join()

exit()
#
# bad_count = 0
# good_count = 0
# for movie in tqdm(Movie.objects.all()):
#     for link in movie.links.values_list('id', 'link'):
#         if is_link_dead(link):
#             MovieLink.objects.get(id=link[0]).delete()
#             # if movie contains no links, delete movie
#             # print('BAD LINK')
#             # print(link)
#             bad_count += 1
#             if bad_count % 100 == 0:
#                 print(bad_count)
#         else:
#             # print('GOOD LINK')
#             # print(link)
#             good_count += 1
#             if good_count % 100 == 0:
#                 print("GOOD {}".format(good_count))
# exit()
#
#
# def scrape_part(link):
#     if is_link_dead(link):
#         return link[0], True
#     else:
#         return link[0], False
#
#
# def scrape():
#     print('scrape')
#     pool_size = cpu_count()
#     pages = list(MovieLink.objects.filter(host__icontains='openload').values_list('id', 'link')[:200])
#     pool = Pool(pool_size)
#     data = pool.map(func=scrape_part, iterable=pages, chunksize=int(len(pages) / pool_size))
#     pool.close()
#     pool.join()
#     # scrape_part(pages[0])
#     from time import sleep
#     sleep(TIMEOUT + 3)
#     return data
#
#
# if __name__ == "__main__":
#     t1 = datetime.now()
#     data = scrape()
#     print(data[:20])
#     print(len(data))
#     delete_ids = [entry[0] for entry in data if entry[1]]
#     MovieLink.objects.filter(pk__in=delete_ids).delete()
#     t2 = datetime.now()
#     total = t2 - t1
#     print("Remove broken links finished in: %s" % total)
