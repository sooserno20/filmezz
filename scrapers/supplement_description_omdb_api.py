import os
import sys
from os.path import abspath, dirname
from urllib.parse import quote

import django
import requests
from tqdm import tqdm

project_path = dirname(dirname(abspath(__file__)))
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'filmezz.settings'
django.setup()

from core.models import Movie
from imdb_data.models import Movie as ImdbMovie

exclude_list = ["24 season 1", "24 season 2", "24 season 3", "24 season 4", "24 season 5", "24 season 6", "24 season 7", "24 season 8", "A Series of Unfortunate Events season 2", "Absentia season 1", "Aftermath season 1", "Alone season 1", "Alone season 3", "Alone season 5", "Animal Kingdom season 1", "Animal Kingdom season 2", "Animal Kingdom season 3", "Bates Motel season 1", "Bates Motel season 2", "Bates Motel season 3", "Bates Motel season 4", "Bates Motel season 5", "Beauty and the Beast season 3", "Beauty and the Beast season 4", "Being Human season 1", "Being Human season 1", "Being Human season 2", "Being Human season 2", "Being Human season 3", "Being Human season 3", "Being Human season 4", "Being Human season 4", "Being Human season 5", "Believe season 1", "Bitten season 1", "Bitten season 2", "Bitten season 3", "Black Lightning season 1", "Black Lightning season 2", "Bones season 1", "Bones season 10", "Bones season 11", "Bones season 12", "Bones season 2", "Bones season 3", "Bones season 4", "Bones season 5", "Bones season 6", "Bones season 7", "Bones season 8", "Bones season 9", "Bordertown season 1", "Broken season 1", "Buffy the Vampire Slayer season 1", "Buffy the Vampire Slayer season 2", "Buffy the Vampire Slayer season 3", "Buffy the Vampire Slayer season 4", "Buffy the Vampire Slayer season 5", "Buffy the Vampire Slayer season 6", "Buffy the Vampire Slayer season 7", "Bulletproof season 1", "Camping season 1", "Class season 1", "Containment season 1", "Conviction season 1", "Daredevil season 1", "Daredevil season 2", "Daredevil season 3", "Dark Angel season 1", "Dark Angel season 2", "Dark Matter season 1", "Dark Matter season 2", "Dark Matter season 3", "Dear White People season 2", "Deception season 1", "Deception season 1", "Defiance season 1", "Defiance season 2", "Defiance season 3", "Desperate Hours season 1", "Doctor Who season 1", "Doctor Who season 10", "Doctor Who season 11", "Doctor Who season 2", "Doctor Who season 3", "Doctor Who season 4", "Doctor Who season 5", "Doctor Who season 6", "Doctor Who season 7", "Doctor Who season 8", "Doctor Who season 9", "Dracula season 1", "Dragon Ball Z season 1", "Dragon Ball Z season 2", "Dragon Ball Z season 3", "Dragon Ball Z season 7", "Dragon Ball season 1", "Dragon Ball season 2", "Dragon Ball season 3", "Empire season 1", "Empire season 2", "Empire season 3", "Empire season 4", "Empire season 5", "Eureka season 1", "Eureka season 2", "Fargo season 1", "Fargo season 2", "Fargo season 3", "Following season 3", "Frequency season 1", "Genius season 2", "Get Shorty season 2", "Hannibal season 1", "Hannibal season 2", "Hannibal season 3", "Happy Together season 1", "Haunted season 1", "Heartbeat season 1", "Heathers season 1", "Impulse season 1", "Instinct season 1", "Justice League season 1", "Justice League season 2", "Justice League season 2", "Last Man Standing season 6", "Last Man Standing season 7", "Legion season 1", "Legion season 2", "Lethal Weapon season 1", "Lethal Weapon season 2", "Lethal Weapon season 3", "Life season 1", "Life season 2", "Lights Out season 1", "Limitless season 1", "Line of Duty season 1", "Line of Duty season 2", "Line of Duty season 3", "Line of Duty season 4", "Little Women season 1", "Lost in Space season 1", "Love season 1", "Love season 2", "Love season 3", "Lovesick season 3", "Maniac season 1", "Max Steel season 1", "Max Steel season 2", "Miami Vice season 1", "Miami Vice season 2", "Miami Vice season 3", "Miami Vice season 4", "Minority Report season 1", "Murder by Numbers season 2", "Nightwatch season 3", "Nightwatch season 4", "Nightwatch season 5", "Notorious season 1", "Once season 1", "Outcast season 1", "Outcast season 2", "Outlander season 1", "Outlander season 2", "Outlander season 3", "Penny Dreadful season 2", "Penny Dreadful season 3", "Playing for Keeps season 1", "Psych season 1", "Psych season 3", "Psych season 4", "Psych season 5", "Psych season 6", "Psych season 7", "Psych season 8", "Pure season 1", "Ransom season 1", "Ransom season 2", "Reasonable Doubt season 2", "Rescue Me season 1", "Rescue Me season 2", "Rescue Me season 3", "Rescue Me season 4", "Rescue Me season 5", "Rescue Me season 6", "Rescue Me season 7", "Resurrection season 1", "Resurrection season 2", "Revenge season 1", "Revenge season 2", "Revenge season 3", "Revenge season 4", "Robin Hood season 1", "Robin Hood season 2", "Robin Hood season 3", "Rogue season 4", "Romper Stomper season 1", "Rookie Blue season 2", "Rookie Blue season 3", "Rookie Blue season 4", "Rookie Blue season 5", "Rookie Blue season 6", "Rosewood season 1", "Rosewood season 2", "Rush Hour season 1", "S.W.A.T. season 1", "S.W.A.T. season 2", "Safe House season 2", "Safe season 1", "School of Rock season 2", "School of Rock season 3", "Second Chance season 1", "Secrets & Lies season 1", "See No Evil season 3", "See No Evil season 4", "Sex and the City season 1", "Sherlock season 1", "Sherlock season 2", "Sherlock season 3", "Sherlock season 4", "Shingeki no kyojin season 1", "Shooter season 1", "Shooter season 2", "Shooter season 3", "Sleepy Hollow season 1", "Sleepy Hollow season 2", "Sleepy Hollow season 3", "Sleepy Hollow season 4", "Snatch season 1", "Spawn season 1-3", "Spider-Man season 1", "Stalingrad season 1", "Stalker season 1", "Supergirl season 1", "Supergirl season 2", "Supergirl season 3", "Supergirl season 4", "Survivor season 33", "Survivor season 34", "Survivor season 35", "Survivor season 36", "Survivor season 37", "Taken season 1", "Taken season 2", "Teen Wolf season 1", "Teen Wolf season 3", "Teen Wolf season 4", "Teen Wolf season 5", "Teen Wolf season 6", "Teenage Mutant Ninja Turtles season 1", "Teenage Mutant Ninja Turtles season 2", "Teenage Mutant Ninja Turtles season 3", "Teenage Mutant Ninja Turtles season 4", "Teenage Mutant Ninja Turtles season 5", "Teenage Mutant Ninja Turtles season 6", "Teenage Mutant Ninja Turtles season 7", "The Bachelor season 21", "The Bachelor season 22", "The Bridge season 1", "The Bridge season 2", "The Brink season 1", "The Butterfly Effect season 1", "The Butterfly Effect season 2", "The Client List season 1", "The Client List season 2", "The Code season 2", "The Collection season 1", "The Contender season 5", "The Crossing season 1", "The Dead Zone season 1", "The Dead Zone season 2", "The Dead Zone season 3", "The Dead Zone season 4", "The Dead Zone season 5", "The Dead Zone season 6", "The Divide season 1", "The Escape Artist season 1", "The Exorcist season 1", "The Exorcist season 2", "The Family season 1", "The Flash season 1", "The Flash season 2", "The Flash season 3", "The Flash season 4", "The Flash season 5", "The Girlfriend Experience season 2", "The Good Doctor season 1", "The Good Doctor season 2", "The Handmaid's Tale season 1", "The Handmaid's Tale season 2", "The Imitation Game season 1", "The Innocents season 1", "The Killing season 1", "The Killing season 2", "The Killing season 3", "The Killing season 4", "The Last Man on Earth season 1", "The Last Man on Earth season 2", "The Last Man on Earth season 3", "The Last Man on Earth season 4", "The Living and the Dead season 1", "The Missing season 2", "The Mist season 1", "The Odd Couple season 3", "The Pact season 1", "The Proposal season 1", "The Punisher season 1", "The Purge season 1", "The Resident season 1", "The Resident season 2", "The Returned season 1", "The Rookie season 1", "The Take season 1", "The Village season 1", "The Village season 2", "The X Files season 1", "The X Files season 10", "The X Files season 11", "The X Files season 2", "The X Files season 3", "The X Files season 4", "The X Files season 9", "Timeline season 2", "Training Day season 1", "Transformers season 1", "Transformers season 2", "Trust season 1", "Türkisch für Anfänger season 1", "Türkisch für Anfänger season 2", "Türkisch für Anfänger season 3", "Underground season 2", "Unforgettable season 1", "Unforgettable season 3", "Unforgettable season 4", "Van Helsing season 1", "Van Helsing season 2", "Van Helsing season 3", "Vanity Fair season 1", "Vice season 5", "Vice season 6", "Victoria season 1", "Victoria season 2", "Wanderlust season 1", "Wanted season 1", "Westworld season 1", "Westworld season 2", "Will season 1", "Wolf Creek season 1", "Wrecked season 1", "Wrecked season 2"]
exclude_set = set()
for movie in exclude_list:
    try:
        exclude_set.add(movie[:movie.index('season')].strip())
    except ValueError:
        pass
exclude_list.extend(exclude_set)
movies_dict = {}

api_key = 'd1b4ba77'
matches = []
for movie in exclude_set:
    im = ImdbMovie.objects.using('imdb').filter(title=movie, title_type__icontains='series').first()
    if im:
        matches.append((im.id, movie))
for match in matches:
    if not Movie.objects.filter(title__icontains=match[1] + ' season'):
        continue
    response = requests.get('http://www.omdbapi.com/?i={}&plot=full&apikey={}'.format(match[0], api_key))
    if response.status_code == 200:
        plot = response.json().get('Plot')
        if not plot:
            continue
        Movie.objects.filter(title__icontains=match[1] + ' season').update(description=plot)
    else:
        print(match)
        exit()

# group the series
for movie in Movie.objects.exclude(title__in=exclude_list):
    if 'season' in movie.title:
        try:
            movies_dict.setdefault(movie.title[:movie.title.index('season')].strip(), [])
            movies_dict[movie.title[:movie.title.index('season')].strip()].append(movie.id)
        except Exception:
            print('"' + movie.title + '"', end=', ')
    else:
        movies_dict[movie.title] = movie.id
print(len(movies_dict))
#api_keys = ['cccd8b10', 'a84076d8', '86808a56', '8525945b', '96677395', '7169db02']
api_keys = ['8a6bb036', 'ada6416c', 'd2a268f6', 'c6ad907d', '3130e990', '124c00f1', 'b4b3a728', 'bf438f8f',
            '38f1ce32', '2b790166', '16f256b9', 'ef58d6e', '2a2c777a', 'b2525faf', 'd078cb33', '212a217f', '117c9473', 'c915e4e5', '64cb8641', 'd1b4ba77']


c = 0
count = 0
found = False
api_key = api_keys.pop()
for movie in movies_dict:
    # c += 1
    # if c < 16050:
    #     continue
    # if movie == 'HK: Hentai Kamen - Abnormal Crisis':
    #     found = True
    # if not found:
    #     continue
    if count % 50 == 0:
        print(count)
    response = requests.get('http://www.omdbapi.com/?t="{}"&plot=full&apikey={}'.format(quote(movie), api_key))
    if response.status_code == 200:
        if isinstance(movies_dict[movie], list):
            for pk in movies_dict[movie]:
                plot = response.json().get('Plot')
                if not plot:
                    continue
                m = Movie.objects.get(pk=pk)
                m.description = plot
                m.save()
                count += 1
        else:
            plot = response.json().get('Plot')
            if not plot:
                continue
            m = Movie.objects.get(pk=movies_dict[movie])
            m.description = plot
            m.save()
            count += 1
    else:
        while response.status_code == 401:
            try:
                api_key = api_keys.pop()
                print(api_key)
            except IndexError:
                print(movie)
                break
            response = requests.get('http://www.omdbapi.com/?t="{}"&plot=full&apikey={}'.format(quote(movie), api_key))
        print(response.content)
        print(movie)
        if isinstance(movies_dict[movie], list):
            for pk in movies_dict[movie]:
                plot = response.json().get('Plot')
                if not plot:
                    continue
                m = Movie.objects.get(pk=pk)
                m.description = plot
                m.save()
                count += 1
        else:
            plot = response.json().get('Plot')
            if not plot:
                continue
            m = Movie.objects.get(pk=movies_dict[movie])
            m.description = plot
            m.save()
            count += 1
print(count)

