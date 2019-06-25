import os
import sys
from datetime import datetime
from os.path import abspath, dirname

import django

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from imdb_data.models import Movie, Name, TitleAlias, TitlePrincipals


def convert_to_none(movie_data):
    return [data if data != r'\N' and data != '\\N\n' else None for data in movie_data]


def import_data(dir):
    # TODO: filter out tvseries which are not parents (title.episode.tsv)
    with open(os.path.join(dir, 'title.basics.tsv')) as title_basics:
        # skip header
        title_basics.readline()
        movies = []
        for line in title_basics:
            try:
                movie_data = convert_to_none(line.split('\t'))
                m = Movie(id=movie_data[0], title_type=movie_data[1], title=movie_data[2], is_adult=movie_data[4],
                          year=movie_data[5], duration=movie_data[7], genres=movie_data[8])
                movies.append(m)
                if len(movies) == 100000:
                    Movie.objects.using('imdb').bulk_create(movies)
                    movies = []
                    print('write')
                    print('1')
            except Exception as e:
                print(e)
                print('1')
        Movie.objects.using('imdb').bulk_create(movies)

    print('DONE1')

    with open(os.path.join(dir, 'title.episode.tsv')) as title_episodes:
        title_episodes.readline()
        parent_movies = []
        for line in title_episodes:
            movie_data = convert_to_none(line.split('\t'))
            parent_movies.append(movie_data[1])
        parent_movies = set(parent_movies)
        Movie.objects.using('imdb').filter(title_type='tvEpisode').exclude(id__in=parent_movies).delete()

    print('DONE1.5')
    with open(os.path.join(dir, 'title.ratings.tsv')) as title_ratings:
        title_ratings.readline()
        count = 0
        exc_count = 0
        for line in title_ratings:
            count += 1
            try:
                movie_data = convert_to_none(line.split('\t'))
                m = Movie.objects.using('imdb').get(id=movie_data[0])
                m.rating = movie_data[1]
                m.save(using='imdb')
            except Exception as e:
                exc_count += 1
        print(count)
        print(exc_count)

    print('DONE2')
    with open(os.path.join(dir, 'title.akas.tsv')) as title_alias:
        title_alias.readline()
        aliases = []
        for line in title_alias:
            try:
                movie_data = convert_to_none(line.split('\t'))
                if not movie_data[3]:
                    continue
                ta = TitleAlias(title_id_id=movie_data[0], title=movie_data[2],
                                region=movie_data[3], original_title=movie_data[7][0] if movie_data[7] else None)
                aliases.append(ta)
                if len(aliases) == 100000:
                    TitleAlias.objects.using('imdb').bulk_create(aliases)
                    aliases = []
                    print('write')
                    print('3')
            except Exception as e:
                print(e)
                print('3')
        TitleAlias.objects.using('imdb').bulk_create(aliases)

    print('DONE3')
    with open(os.path.join(dir, 'name.basics.tsv')) as name_basics:
        name_basics.readline()
        names = []
        for line in name_basics:
            try:
                movie_data = convert_to_none(line.split('\t'))
                n = Name(id=movie_data[0], name=movie_data[1])
                names.append(n)
                if len(names) == 100000:
                    Name.objects.using('imdb').bulk_create(names)
                    names = []
                    print('write')
                    print('4')
            except Exception as e:
                print(e)
                print('4')
        Name.objects.using('imdb').bulk_create(names)

    print('DONE4')
    with open(os.path.join(dir, 'title.principals.tsv')) as title_principals:
        title_principals.readline()
        principals = []
        for line in title_principals:
            try:
                movie_data = convert_to_none(line.split('\t'))
                tp = TitlePrincipals(movie_id=movie_data[0], name_id=movie_data[2], category=movie_data[3])
                principals.append(tp)
                if len(principals) == 100000:
                    TitlePrincipals.objects.using('imdb').bulk_create(principals)
                    principals = []
                    print('write')
                    print('5')
            except Exception as e:
                print(e)
                print('5')
        TitlePrincipals.objects.using('imdb').bulk_create(principals)

    print('DONE5')


if __name__ == '__main__':
    if not os.path.exists(sys.argv[1]):
        print('Directory does not exist')
    t1 = datetime.now()
    # uuids = [obj.uuid for obj in cls.objects.all()]
    # with MultiProcess() as mp:
    #     mp.map(update_index_for_uuid, uuids)
    #     results = mp.results()
    import_data(sys.argv[1])
    t2 = datetime.now()
    total = t2 - t1
    print("Import finished in: %s" % total)
