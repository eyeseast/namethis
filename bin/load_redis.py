#!/usr/bin/env python
"""
Load names from sqlite database into redis
"""
from __future__ import unicode_literals

import sys
import dataset
from redis import StrictRedis

DATABASE_URL = "sqlite:///names.db"
DEFAULT_REDIS_URL = "redis://localhost:6379/1"
TABLE_NAME = "names"

def main(db_url, redis_url):
    """
    Fetch from DB. Load to redis.
    """
    db = dataset.connect(db_url)
    table = db[TABLE_NAME]
    redis = StrictRedis.from_url(redis_url)
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        redis_url = sys.argv[1]
    else:
        redis_url = DEFAULT_REDIS_URL

    main(DATABASE_URL, redis_url)