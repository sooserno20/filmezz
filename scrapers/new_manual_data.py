import json
import csv
import os
import sys
from os.path import abspath, dirname

import django
import urllib3

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()
urllib3.disable_warnings()
from core.models import Movie, MovieLink
with open('new_data.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter='|', quotechar='"')
    # skip header
    reader.__next__()
    for row in reader:
        row = [s.strip() for s in row]
        name, is_series, image_url, imdb_score, categories, actors, \
        directors, translation, year, duration, links, desc = row

        name += 'TESTTT'

        if Movie.objects.filter(title=name):
            continue

        # m = Movie.objects.create(title=name, description=desc, image_url=image_url, is_series=is_series,
        #                          imdb_score=imdb_score, year=year, duration=duration)

        # links = json.loads(links)
        # for link in links:
        #     MovieLink.objects.create(movie=m, host=link['host'], link=link['link'])