import os
import sys
from os.path import abspath, dirname

import django

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from core.models import Category, Movie


Movie.objects.filter(links__isnull=True).delete()
# filmezz.eu user avatars
Movie.objects.filter(image_url__icontains='eu/avatar').update(image_url='')
Category.objects.filter(movies__isnull=True).delete()

CATEGORY_DICT = {'romantikus': 'Romance', 'vígjáték': 'Comedy', 'krimi': 'Crime', 'háborús': 'War',
                 'katasztrófafilm': 'Disaster', 'zenés': 'Music', 'misztikus': 'Mystery', 'animáció': 'Animation',
                 'dráma': 'Drama', 'történelmi': 'history', 'családi': 'Family', 'akció': 'Action',
                 'dokumentum': 'Documentary', 'tv-sorozat': 'TV Series', 'életrajzi': 'Biography',
                 'ázsiai': 'Asian', 'kaland': 'Adventure', 'magyar film': 'Hungarian'}

for category in Category.objects.all():
    if category.name.lower() in CATEGORY_DICT:
        category.name = CATEGORY_DICT[category.name.lower()]
        category.save()
