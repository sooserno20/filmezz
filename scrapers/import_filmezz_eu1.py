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


def import_filmezz_eu():
    with open(sys.argv[1]) as data:
        json_data = json.loads(data.read())
    for line in json_data:
        for key in line:
            entry = line[key]
            entry['name'] = key
            try:
                entry['name'] = entry['name'].strip()
                year = entry['year']
                try:
                    imdb_score = float(entry['imdb_score'])
                except ValueError:
                    imdb_score = 0
                m, created = Movie.objects.get_or_create(title=key, description=entry['description'],
                                                         image_url=entry['image_path'], year=year,
                                                         imdb_score=imdb_score, is_series=entry['is_series'])
                for link in entry['links']:
                    try:
                        episode_nr = int(link['info'].split('.')[0])
                    except ValueError:
                        episode_nr = link['info']
                    m.links.get_or_create(host=link['host'], language=link['language'],
                                          link=link['link'], episode_nr=episode_nr)
                for director in entry['directors']:
                    d, created = Director.objects.get_or_create(name=director)
                    m.directors.add(d)
                for actor in entry['actors']:
                    a, created = Actor.objects.get_or_create(name=actor.split('(')[0].strip())
                    m.actors.add(a)
                for category in entry['genres']:
                    c, created = Category.objects.get_or_create(name=category)
                    m.categories.add(c)
            except Exception as e:
                print("Error: {} for {}".format(str(e), entry['name']))
                try:
                    m.delete()
                except Exception:
                    pass


if __name__ == '__main__':
    t1 = datetime.now()
    import_filmezz_eu()
    t2 = datetime.now()
    total = t2 - t1
    print("Import finished in: %s" % total)
