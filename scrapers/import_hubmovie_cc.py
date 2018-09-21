import os
from datetime import datetime
from os.path import abspath, dirname

import django
import sys

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

import json
import sys
from cloudinary.uploader import upload

from core.models import Movie, Director, Actor, Category


def import_hubmovie_cc():
    with open(sys.argv[1]) as data:
        json_data = json.loads(data.read())
    for line in json_data:
        for key, entry in line.items():
            try:
                name = key
                year = entry['year']
                try:
                    imdb_score = float(entry['imdb_score'])
                except:
                    imdb_score = 0
                    # TODO: for now skip entries with incomplete info, if imdb info scraper is complete remove continue
                    # continue

                # !!!!!!!!! TODO: scrape series too and solve this
                entry['is_series'] = False
                if entry['is_series']:
                    m, created = Movie.objects.get_or_create(title=name, description=entry['description'], year=year,
                                                             image_url=entry['image_path'], imdb_score=imdb_score)
                    for episode, links in json.loads(entry['links']).items():
                        episode_nr = episode.split('.')[0]
                        for host, link in links.items():
                            m.links.get_or_create(host=host, episode_nr=episode_nr, language=link[0][1], link=link[0][0])
                else:
                    m, created = Movie.objects.get_or_create(title=name, description=entry['description'],
                                                             image_url='http://www.hubmovie.cc' + entry['image_path'][1:],
                                                             imdb_score=imdb_score, year=year)
                    for link in entry['links']:
                        m.links.get_or_create(host=link['host'], link=link['link'][2:-1])  # strip b''
                if entry['directors']:
                    d, created = Director.objects.get_or_create(name=entry['directors'][0])
                    m.directors.add(d)
                for actor in entry['actors']:
                    a, created = Actor.objects.get_or_create(name=actor)
                    m.actors.add(a)
                for category in entry['genres']:
                    if category.strip().lower() != name.strip().lower():
                        c, created = Category.objects.get_or_create(name=category)
                        m.categories.add(c)
            except Exception as e:
                print("Error: {} for {}".format(str(e), key))
                try:
                    m.delete()
                except Exception:
                    pass


if __name__ == '__main__':
    t1 = datetime.now()
    import_hubmovie_cc()
    t2 = datetime.now()
    total = t2 - t1
    print("Import finished in: %s" % total)
