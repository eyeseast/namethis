"""
Flask app serving up random names for no good reason
"""
import os
import dataset
from flask import Flask, g, render_template, jsonify
from redis import StrictRedis

# using this for prototyping
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///names.db')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

app = Flask(__name__)
app.config.from_object(__name__)


def get_db():
    "Connect to DB"
    db = g.get('db', None)
    if db is None:
        db = dataset.connect(DATABASE_URL)
    return db


def get_redis():
    "Get a redis connection"
    redis = g.get('redis', None)
    if redis is None:
        redis = StrictRedis.from_url(REDIS_URL)
    return redis


@app.route('/')
def index():
    "Get us started"
    return render_template('index.html')


@app.route('/name')
@app.route('/name/<group>')
def get_random_name(group=None):
    "Get a random name"
    redis = get_redis()
    if group in ('f', 'm', 'all'):
        key = "names:{}".format(group)
    else:
        key = "names:all"

    return redis.srandmember(key)


@app.route('/names')
@app.route('/names/<group>')
def get_random_stats(group=None):
    "Get a random name, with stats"
    name = get_random_name(group=group)
    stats = get_name_stats(name, sex=group)
    return jsonify(name=name, stats=stats)


@app.route('/<name>')
@app.route('/<name>/<sex>')
def name_stats(name, sex=None):
    "Get JSON stats for a single name"
    stats = get_name_stats(name, sex)
    return jsonify(results=stats)


def get_name_stats(name, sex=None):
    "Get stats for a single name"
    db = get_db()
    table = db['names']
    where = {'name': name}
    if sex:
        where['sex'] = sex.upper()

    result = table.find(**where)
    return list(result)


if __name__ == "__main__":
    app.run(debug=True)