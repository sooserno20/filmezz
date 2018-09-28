import os
from datetime import datetime
from os.path import abspath, dirname

import django
import sys

import requests

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from cloudinary.uploader import upload

from core.models import Movie


def upload_images():
    count = 0
    for movie in Movie.objects.all():
        try:
            if movie.image_url.find('cloudinary') != -1:
                continue
            response = requests.get(movie.image_url)
            file_name = movie.image_url.split('/')[-1]
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
            else:
                print('Name: {}, status: {}'.format(movie.title, response.status_code))

            response = upload(file_name, public_id='movie_images/' + file_name.split('.')[0])
            movie.image_url = response['url']
            movie.save()
            os.remove(file_name)
            count += 1
            if count % 300 == 0:
                print('{} movies processed'.format(count))
        except Exception as e:
            print('Exc {}'.format(str(e)))
            try:
                print('Error for {} with exc {}'.format(m, str(e)))
            except NameError:
                pass


if __name__ == '__main__':
    t1 = datetime.now()
    upload_images()
    t2 = datetime.now()
    total = t2 - t1
    print("Upload finished in: %s" % total)
