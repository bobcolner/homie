"""homeie.py

Fetches the content URLs on a given homepage.

Usage:
    homeie.py [options]
    homeie.py -h | --help

Options:
    -h  --help              Show this screen
    --homepage <homepage>   homepage to scrape [default: https://injo.com/]
    --db-user <user>        db username [default: postgres]
    --db-pass <pass>        db password
    --db-host <host>        db hostname [default: localhost]
    --db-port <port>        db port [default: 5432]
    --db-name <name>        db name [default: postgres]
"""
import os
import datetime
import time
import json
from docopt import docopt
import requests
from lxml import html
from pgrap import pgkv

def get_homepage_urls(url):
    resp = requests.get(url)
    doc = html.fromstring(resp.text)
    hrefs = list(set([ a.attrib.get('href') for a in doc.cssselect('a') ]))
    hrefs = [ url for url in hrefs if url != None ]
    hrefs = [ url for url in hrefs if url.startswith('//') ]
    return {
        'craw_time': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
        'content_urls': [ 'https:' + url for url in hrefs if not url.startswith('//about') ]
    }

def save_json_file(results, path='./'):
    with open(path+'earls.json', 'a') as fio:
        fio.writelines(json.dumps(results)+'\n')

def insert_pg_kv(conn, results):
    pgkv.insert_kv(conn, k_data=results['craw_time'], v_data=results, table='injo', schema='homeie', dtype='jsonb', setup='create')


if __name__ == '__main__':

    args = docopt(__doc__)
    
    conn = pgkv.pgrap.psycopg2.connect(
        user=args['--db-user'],
        password=args['--db-pass'],
        host=args['--db-host'],
        port=args['--db-port'],
        database=args['--db-name']
        )
    conn.autocommit = True

    while True:
        earls = get_homepage_urls(url=args['--homepage'])
        print(earls)
        save_json_file(earls)
        insert_pg_kv(conn, earls)
        time.sleep(300)
