import os
from datetime import datetime
from os.path import abspath, dirname

import django
import sys

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

import sys
from cloudinary.uploader import upload

from core.models import Movie


def upload_images():
    directory = sys.argv[1]
    print('Directory: ' + directory)
    for image in os.listdir(directory):
        try:
            # TODO: Download images and upload directly to cloudinary
            m = Movie.objects.filter(image_url__endswith=image).first()
            if not m:
                print('Image for movie not found {}'.format(image))
                continue
            response = upload(os.path.join(directory, image), public_id='images/' + image.split('.')[0])
            m.image_url = response['url']
            m.save()
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
