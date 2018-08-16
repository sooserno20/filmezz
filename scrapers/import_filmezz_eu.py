from os import environ
environ.setdefault("DJANGO_SETTINGS_MODULE", "filmezz.settings")
import django
django.setup()

import json
import sys
from json import JSONDecodeError
from cloudinary.uploader import upload

from core.models import Movie


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
        if entry['is_series']:
            # skip series for now
            continue

        m = Movie(title=entry['name'], description=entry['description'])
        m.image = upload(file=entry['image_path'])['url']
        m.save()
        for key, link in json.loads(entry['links']).items():
            m.movielink_set.create(link=link[0])


if __name__ == '__main__':
    import_filmezz_eu()
