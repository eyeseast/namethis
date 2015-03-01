#!/usr/bin/env python
"""
Load names from sqlite database into redis
"""
from __future__ import unicode_literals

import argparse
import itertools
import sys
import dataset
from redis import StrictRedis

DEFAULT_DATABASE_URL = "sqlite:///names.db"
DEFAULT_REDIS_URL = "redis://localhost:6379/1"
TABLE_NAME = "names"

RANKS = [5, 50, 500, 1000]

def main(db_url, redis_url, flush=False):
    """
    Fetch from DB. Load to redis.
    """
    db = dataset.connect(db_url)
    table = db[TABLE_NAME]
    redis = StrictRedis.from_url(redis_url)

    # flush or not
    if flush:
        print('Flushing database at {}'.format(redis_url))
        redis.flushdb()

    # pipeline lots of things
    pipe = redis.pipeline()

    # all names
    for row in table.distinct('name'):
        pipe.sadd('names:all', row['name'])

    pipe.execute()

    # girls
    for row in table.distinct('name', sex='F'):
        pipe.sadd('names:f', row['name'])

    pipe.execute()

    # boys
    for row in table.distinct('name', sex='M'):
        pipe.sadd('names:m', row['name'])

    pipe.execute()

    # popularity
    for sex, rank in itertools.product(['F', 'M'], RANKS):
        sql = "SELECT distinct(name) FROM {} WHERE sex = :sex AND rank <= :rank".format(TABLE_NAME)
        print('Loading: {sex}, {rank}'.format(sex=sex, rank=rank))

        for row in db.query(sql, sex=sex, rank=rank):
            key = ':'.join(['names', sex.lower(), str(rank)])
            pipe.sadd(key, row['name'])

        # execute for each combination
        pipe.execute()

    # store the unions
    for rank in RANKS:
        pipe.sunionstore(
            'names:all:{}'.format(rank),
            'names:f:{}'.format(rank),
            'names:m:{}'.format(rank)
        )

    pipe.execute()

# arg parsing
parser = argparse.ArgumentParser(
    description='Load aggregates from a database into redis')

parser.add_argument('database_uri', default=DEFAULT_DATABASE_URL,
    help='Connection URI for source database')

parser.add_argument('redis_uri', default=DEFAULT_REDIS_URL,
    help='Connection URI for redis client')

parser.add_argument('--flush', default=False, action='store_true')

if __name__ == "__main__":

    args = parser.parse_args()
    main(args.database_uri, args.redis_uri, args.flush)
