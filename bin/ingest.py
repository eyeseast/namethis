#!/usr/bin/env python
"""
Load name files into a database for analysis

Each file is a csv named yobYYYY.txt, with no headers:
    Name,Sex,Count

"""
from __future__ import division
from __future__ import unicode_literals

import csv
import os
import sys

import dataset

BIN = os.path.dirname(__file__)
ROOT = os.path.dirname(BIN)
DATA_DIR = os.path.join(ROOT, 'data', 'names')

TABLE_NAME = "names"

def main(uri):
    """
    Connect to and load the actual database
    """
    db = dataset.connect(uri)
    
    # drop if exists then insert many
    if TABLE_NAME in db:
        print('Table "{}" exists. Dropping.'.format(TABLE_NAME))
        db.op.drop_table(TABLE_NAME)

    # get or create table
    table = db[TABLE_NAME]

    for year in range(1880, 2014):
        print('Loading {}'.format(year))
        data = process_year(year)
        table.insert_many(data)

    table.create_index(['name', 'sex'])


def process_year(year):
    """
    Read data for a single year and yield rows of processed data
    """
    filename = "yob{}.txt".format(year)
    filename = os.path.join(DATA_DIR, filename)

    # we need a couple passes on this data, so just read it once
    # and be done with it
    with open(filename) as f:
        data = list(csv.reader(f))

    # get a total for this year
    total = sum(int(row[2]) for row in data)

    # sort by count, filter by sex
    data.sort(key=lambda row: int(row[2]), reverse=True)
    boys = (row for row in data if row[1] == 'M')
    girls = (row for row in data if row[1] == 'F')

    for group in [girls, boys]:
        for i, row in enumerate(group, 1):
            name, sex, number = row
            number = int(number)
            yield {
                'year': year,
                'name': name,
                'sex': sex,
                'number': number,
                'rank': i,
                'percent': number / total
            }


if __name__ == "__main__":
    main(sys.argv[1])