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

from core.models import Movie, MovieTranslation


def update_filmezz_eu():
    with open(sys.argv[1]) as data:
        json_data = json.loads(data.read())
    for line in json_data:
        for key in line:
            entry = line[key]
            try:
                if entry['english_name'] == 'Linkek a filmhez':
                    continue
                m = Movie.objects.get(title=key, year=entry['year'])
                if m.is_series:
                    if 'season' in entry['english_name'].lower():
                        m.title = entry['english_name']
                    else:
                        # print(key)
                        lower_name = key.lower()
                        try:
                            season_nr = key[:lower_name.index('évad')].strip().split(' ')[-1].split('.')[0]
                        except ValueError:
                            m.title = entry['english_name']
                            continue
                        m.title = entry['english_name'].strip() + ' season ' + season_nr
                        # print(m.title)
                else:
                    m.title = entry['english_name']
                m.save()
                mo = MovieTranslation(movie=m, language='Hungarian', title=key)
                mo.save()
            except Movie.DoesNotExist:
                print('Doesnotexist' + key)
            except Movie.MultipleObjectsReturned:
                print("EXC" + key + ' ' + entry['english_name'])
            except Exception:
                print("EXCCCCCCC" + key + ' ' + entry['english_name'])


if __name__ == '__main__':
    t1 = datetime.now()
    update_filmezz_eu()
    t2 = datetime.now()
    total = t2 - t1
    print("Import finished in: %s" % total)
