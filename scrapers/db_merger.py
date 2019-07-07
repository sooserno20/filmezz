import os
import sys
from os.path import abspath, dirname

import django
from django.db import OperationalError

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from core.models import Movie, Director, Actor, Category

try:
    Movie.objects.using('db2').count()
except OperationalError:
    print('Db2 does not exist')

movies = []


def create_movie(movie):
    m = Movie.objects.create(title=movie.title, description=movie.description, image_url=movie.image_url,
                             is_series=movie.is_series, imdb_score=movie.imdb_score, year=movie.year,
                             duration=movie.duration)
    for actor in movie.actors.all():
        a = Actor.objects.filter(name__iexact=actor.name).first()
        m.actors.add(a)
    for director in movie.directors.all():
        d = Director.objects.filter(name__iexact=director.name).first()
        m.directors.add(d)
    for category in movie.categories.all():
        c = Category.objects.filter(name__iexact=category.name).first()
        m.categories.add(c)
    for link in movie.links.all():
        m.links.get_or_create(host=link.host, episode_nr=link.episode_nr, language=link.language, link=link.link)
    for translation in movie.translations.all():
        m.translations.get_or_create(title=translation.title, language=translation.language)


def update_movie(old_movie, new_movie):
    for link in new_movie.links.all():
        old_movie.links.get_or_create(host=link.host, episode_nr=link.episode_nr, language=link.language,
                                      link=link.link)


for category in Category.objects.using('db2').all():
    try:
        Category.objects.get(name__iexact=category.name.lower())
    except Category.DoesNotExist:
        Category.objects.create(name=category.name.capitalize())
    except Category.MultipleObjectsReturned:
        print('Multiple objects for: ' + category.name)

for actor in Actor.objects.using('db2').all():
    try:
        m = Actor.objects.get(name__iexact=actor.name.lower())
    except Actor.DoesNotExist:
        Actor.objects.create(name=actor.name.title())
    except Actor.MultipleObjectsReturned:
        print('Multiple objects for: ' + actor.name)

for director in Director.objects.using('db2').all():
    try:
        m = Director.objects.get(name__iexact=director.name.lower())
    except Director.DoesNotExist:
        Director.objects.create(name=director.name.title())
    except Director.MultipleObjectsReturned:
        print('Multiple objects for: ' + director.name)

count = 0
count_create = 0
for movie in Movie.objects.using('db2').all():
    try:
        m = Movie.objects.get(title__iexact=movie.title.lower())
    except Movie.DoesNotExist:
        create_movie(movie)
        count_create += 1
    except Movie.MultipleObjectsReturned:
        print('Multiple objects for: ' + movie.title)
        count += 1
    else:
        update_movie(m, movie)
        count += 1

print('Existing movies {}'.format(count))
print('New movies {}'.format(count_create))
