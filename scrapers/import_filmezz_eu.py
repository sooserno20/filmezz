import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

import json
import sys
from json import JSONDecodeError
from cloudinary.uploader import upload

from core.models import Movie, Director, Actor, Category


def import_filmezz_eu():
    with open(sys.argv[1]) as data:
        # for line in data:
        #     try:
        #         if line[-1] == '\n':
        #             line = line[:-1]
        #         if line[-1] == ',':
        #             line = line[:-1]
        #
        #         entry = json.loads(line)
        #     except JSONDecodeError:
        #         pass
        #     else:
        #         print(entry)
        json_data = json.loads(data.read())
    for entry in json_data[:50]:
        try:
            if entry['is_series']:
                m = Movie(title=entry['name'], description=entry['description'], image_url=entry['image_path'])
                m.save()
                for episode, links in json.loads(entry['links']).items():
                    episode_nr = episode.split('.')[0]
                    for host, link in links.items():
                        m.links.create(episode_nr=episode_nr, link=link[0])
            else:
                m = Movie(title=entry['name'], description=entry['description'], image_url=entry['image_path'])
                m.save()
                for host, link in json.loads(entry['links']).items():
                    m.links.create(link=link[0])
            d, created = Director.objects.get_or_create(name=entry['director'])
            m.directors.add(d)
            for actor in json.loads(entry['actors']):
                a, created = Actor.objects.get_or_create(name=actor)
                m.actors.add(a)
            for category in json.loads(entry['categories']):
                c, created = Category.objects.get_or_create(name=category)
                m.categories.add(c)
        except Exception:
            try:
                m.delete()
            except Exception:
                pass


if __name__ == '__main__':
    import_filmezz_eu()
