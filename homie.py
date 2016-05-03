"""homie.py

Fetches the content URLs on a given homepage.

Usage:
    homie.py [options]
    homie.py -h | --help

Options:
    -h  --help              Show this screen
    --homepage <homepage>   homepage to scrape [default: https://injo.com/]
    --db-user <user>        db username [default: postgres]
    --db-pass <pass>        db password
    --db-host <host>        db hostname [default: localhost]
    --db-port <port>        db port [default: 5432]
    --db-name <name>        db name [default: postgres]
    --db-table <table>      db table [default: default]
"""
import os
import datetime
import time
import json
from docopt import docopt
import requests
from lxml import html
from pgrap import pgkv

args = docopt(__doc__)

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

def insert_pg_kv(conn, data, table):
    pgkv.insert_kv(conn, k_data=data['craw_time'], v_data=data, table=table, schema='homie', dtype='jsonb', setup='create')
    
def pg_connect():    
    conn = pgkv.pgrap.psycopg2.connect(
        user=args['--db-user'],
        password=args['--db-pass'],
        host=args['--db-host'],
        port=args['--db-port'],
        database=args['--db-name']
        )
    conn.autocommit = True
    return conn

if __name__ == '__main__':

    while True:

        try:
            earls = get_homepage_urls(url=args['--homepage'])
            print(earls)
            save_json_file(earls)
            if args['--db-pass']:
                conn = pg_connect()
                insert_pg_kv(conn, data=earls, table=args['--db-table'])
                conn.close()
            time.sleep(300)
        
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            save_json_file(str(e))
            if conn:
                conn.close()
            continue
