import os
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
    for entry in json_data[:50]:
        try:
            entry['name'] = entry['name'].strip()
            if entry['name'][-1] == ')' and entry['name'][-6] == '(':
                name = entry['name'][:-6]
                year = entry['name'][-5:-1]
            else:
                name = entry['name']
                year = ''
            if entry['is_series']:
                m, created = Movie.objects.get_or_create(title=name, description=entry['description'],
                                                         image_url=entry['image_path'], year=year)
                for episode, links in json.loads(entry['links']).items():
                    episode_nr = episode.split('.')[0]
                    for host, link in links.items():
                        m.links.get_or_create(host=host, episode_nr=episode_nr, language=link[0][1], link=link[0][0])
            else:
                m, created = Movie.objects.get_or_create(title=name, description=entry['description'],
                                                         image_url=entry['image_path'],
                                                         imdb_score=float(entry['imdb_score']), year=year)
                for host, link in json.loads(entry['links']).items():
                    m.links.get_or_create(host=host, language=link[0][1], link=link[0][0])
            d, created = Director.objects.get_or_create(name=entry['director'])
            m.directors.add(d)
            for actor in json.loads(entry['actors']):
                a, created = Actor.objects.get_or_create(name=actor)
                m.actors.add(a)
            for category in json.loads(entry['categories']):
                c, created = Category.objects.get_or_create(name=category)
                m.categories.add(c)
        except Exception as e:
            print("Error: {} for {}".format(str(e), entry['name']))
            try:
                m.delete()
            except Exception:
                pass


if __name__ == '__main__':
    import_filmezz_eu()
