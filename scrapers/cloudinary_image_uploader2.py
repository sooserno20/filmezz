import os
from datetime import datetime
from os.path import abspath, dirname
import unicodedata
import django
import sys

import requests

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from cloudinary.uploader import upload

from core.models import Movie

MAPPING_FILE = open('movie_image_mappings.txt', 'a+', encoding='utf-8')


def upload_images():
    count = 0
    count_already_processed = 0
    for movie in Movie.objects.all():
        try:
            if not movie.image_url:
                continue
            if movie.image_url.find('cloudinary') != -1:
                count_already_processed += 1
                if count_already_processed % 300 == 0:
                    print('{} movies already processed'.format(count_already_processed))
                continue

            file_name = os.path.join(dirname(dirname(abspath(__file__))), 'media', 'movie_images', str(movie.image_url).
                                     split('/')[-1])
            if not os.path.exists(file_name) or \
                    file_name != unicodedata.normalize('NFKD', file_name).encode('ASCII', 'ignore').decode('ASCII'):
                response = requests.get(movie.image_url)
                file_name = movie.image_url.split('/')[-1]
                # normalize accented characters
                file_name = unicodedata.normalize('NFKD', file_name).encode('ASCII', 'ignore').decode('ASCII')
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                elif response.status_code == 404:
                    movie.image_url = None
                    movie.save()
                    continue
                else:
                    print('Name: {}, status: {}'.format(movie.title, response.status_code))
                    continue

            response = upload(file_name, public_id='movie_images/' + file_name.split('/')[-1].split('.')[0])
            MAPPING_FILE.write('{},{}\n'.format(movie.image_url, response['url']))
            movie.image_url = response['url']
            # os.remove(file_name)
            movie.save()
            count += 1
            if count % 100 == 0:
                print('{} movies processed'.format(count))
        except Exception as e:
            print('Exc {}'.format(str(e)))
            try:
                print('Error for {} with exc {}'.format(movie.title, str(e)))
            except NameError:
                pass
        print('{} movies processed'.format(count))


if __name__ == '__main__':
    t1 = datetime.now()
    upload_images()
    t2 = datetime.now()
    total = t2 - t1
    print("Upload finished in: %s" % total)
    MAPPING_FILE.close()
