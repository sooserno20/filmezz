import os
import sys
from datetime import datetime
from difflib import SequenceMatcher
from os.path import abspath, dirname

import django
from tqdm import tqdm

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from imdb_data.models import Movie as ImdbMovie, TitleAlias, TitlePrincipals

from core.models import Movie, MovieTranslation, Category


def get_value_or_empty(year):
    if year:
        return str(year)
    return ''


def get_matching_ids():
    imdb_movies = {imdb_movie[1].strip().lower() + get_value_or_empty(imdb_movie[2]): imdb_movie[0]
                   for imdb_movie in ImdbMovie.objects.using('imdb').values_list('id', 'title', 'year')}
    movies = [(movie[0], movie[1].strip().lower(), movie[2], movie[3]) for movie in
              Movie.objects.values_list('id', 'title', 'translations__title', 'year')]
    count = 0
    match_pairs = []
    for movie in movies[:]:
        title = movie[1]
        try:
            # cut season nr from series (added in importers)
            title = title[:title.index('season')].strip()
        except ValueError:
            pass
        if movie[3]:
            title += movie[3]
        if title in imdb_movies:
            match_pairs.append((imdb_movies[title], movie[0]))
            imdb_movies.pop(title)
            movies.remove(movie)
            count += 1
    print('Matched pairs')
    print(count)

    # alias_movies = {imdb_movie[1].strip().lower(): imdb_movie[0] for imdb_movie in
    #                 TitleAlias.objects.using('imdb').values_list('title_id_id', 'title')}
    # for movie in movies[:]:
    #     translation = movie[2]
    #     if translation:
    #         translation = translation.strip().lower()
    #     else:
    #         continue
    #     if translation in alias_movies:
    #         match_pairs.append((alias_movies[translation], movie[0]))
    #         movies.remove(movie)
    #         count += 1
    #
    # print(count)
    # for movie in tqdm(movies):
    #     for name_key in alias_movies:
    #         translation = movie[2]
    #         if translation:
    #             translation = translation.strip().lower()
    #         else:
    #             continue
    #         if translation[:3] == name_key[:3] and SequenceMatcher(a=translation, b=name_key).ratio() > 0.9:
    #             count += 1
    #             match_pairs.append((alias_movies[name_key], movie[0]))
    #             print(name_key)
    #             print(translation)
    #             break
    # print(count)

    return match_pairs


def supplement_db_data():
    matches = get_matching_ids()

    for match in tqdm(matches):
        movie = Movie.objects.get(id=match[1])
        imdb_movie = ImdbMovie.objects.using('imdb').get(id=match[0])
        if imdb_movie.rating:
            movie.imdb_score = imdb_movie.rating
        movie.duration = imdb_movie.duration
        if imdb_movie.year:
            movie.year = imdb_movie.year
        movie.save()
        if imdb_movie.genres:
            genres = imdb_movie.genres[:-1].lower().split(',')
            movie.categories.clear()
            for genre in genres:
                movie.categories.get_or_create(name=genre)

        aliases = TitleAlias.objects.using('imdb').filter(title_id_id=imdb_movie.id)
        if aliases:
            MovieTranslation.objects.filter(movie=movie).delete()
            translations = []
            for alias in aliases:
                translations.append(MovieTranslation(movie_id=movie.id, title=alias.title.strip(),
                                                     language=alias.region))
            movie.translations.bulk_create(translations)

        principals = TitlePrincipals.objects.filter(movie=imdb_movie)
        if principals:
            for principal in principals:
                if principal.category == 'director':
                    movie.directors.clear()
                    break
            for principal in principals:
                if principal.category == 'actor' or principal.category == 'actress' or principal.category == 'self':
                    movie.actors.clear()
                    break
            for principal in principals:
                if principal.category == 'director':
                    movie.directors.get_or_create(name=principal.name.name.strip())
                if principal.category == 'actor' or principal.category == 'actress' or principal.category == 'self':
                    movie.actors.get_or_create(name=principal.name.name.strip())


if __name__ == '__main__':
    t1 = datetime.now()
    supplement_db_data()
    t2 = datetime.now()
    total = t2 - t1
    print("Supplement finished in: %s" % total)
