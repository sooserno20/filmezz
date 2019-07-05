# scrape from filmezz, hubmovie, mv db to db2(for later merging), python migrate, import filmezz, hubmovie,
# remove links, imdb, omdb supplement, optional: image urls, merge
# TODO: parallelization
# parallel: scrape filmezz, hubmovie
# parallel: remove links, imdb
# BACKUP: first db, second db after imports and before merging, import files, movies_crawled (copy in new folder)
# TODO: archive backups
# TODO: image uploader: use movie_image_mappings.txt to map images already uploaded

import subprocess
import sys
from datetime import datetime

FILMEZZ_DATA_FILE = 'filmezz_eu8.json'
HUBMOVIE_DATA_FILE = 'hubmovie_cc5.json'

# PREPARATIONS
# make backup dir
dir_name = str(datetime.now())
subprocess.call(["mkdir", dir_name])
# if there is move error STOP
if subprocess.call(["mv", "../db.sqlite3", "../db_big.sqlite3"]):
    print('First db does not exist')
    sys.exit(1)
# backup first db
subprocess.call(["cp", "../db_big.sqlite3", dir_name])
# create new db
subprocess.call(["python", "../manage.py", "migrate"])
# cleanup
try:
    subprocess.call(["rm", FILMEZZ_DATA_FILE])
    subprocess.call(["rm", HUBMOVIE_DATA_FILE])
except Exception:
    pass

# SCRAPE
# TODO: update serials
if subprocess.call(["python", "scrape_filmezz_eu6.py"]):
    print('Filmezz scraper failed')
    sys.exit(1)
subprocess.call(["cp", FILMEZZ_DATA_FILE, dir_name])
# TODO: update serials
if subprocess.call(["python", "scrape_hubmovie_cc4.py"]):
    print('Hubmovie scraper failed')
    sys.exit(1)
subprocess.call(["cp", HUBMOVIE_DATA_FILE, dir_name])

# IMPORT
if subprocess.call(["python", "import_filmezz_eu1.py", FILMEZZ_DATA_FILE]):
    print('Filmezz import failed')
    sys.exit(1)
if subprocess.call(["python", "import_hubmovie_cc.py", HUBMOVIE_DATA_FILE]):
    print('Hubmovie import failed')
    sys.exit(1)
subprocess.call(["cp", "../db.sqlite3", dir_name + '/db_imported.sqlite3'])

# PROCESS
subprocess.call(["python", "remove_broken_links.py"])
subprocess.call(["python", "../imdb_data/supplement_db_data.py"])
subprocess.call(["python", "supplement_description_omdb_api.py"])
# subprocess.call(["python", "cloudinary_image_uploader2.py"])
subprocess.call(["cp", "../db.sqlite3", dir_name + '/db_processed.sqlite3'])
subprocess.call(["python", "cleanup_db.py"])

# MERGE
subprocess.call(["mv", "../db.sqlite3", "../db2.sqlite3"])
subprocess.call(["mv", "../db_big.sqlite3", "../db.sqlite3"])
subprocess.call(["python", "db_merger.py"])

# CLEANUP
subprocess.call(["rm", FILMEZZ_DATA_FILE])
subprocess.call(["rm", HUBMOVIE_DATA_FILE])
subprocess.call(["rm", "../db2.sqlite3"])
