"""
Flask app serving up random names for no good reason
"""
import os
import dataset
from flask import Flask, g, render_template, jsonify, url_for
from redis import StrictRedis

# database
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///names.db')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

DATABASE_ENGINE_KWARGS = {
    'pool_recycle': 3600
}

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


def get_name_stats(name, sex=None):
    "Get stats for a single name"
    db = get_db()
    table = db['names']
    where = {'name': name}
    if sex in {'m', 'M', 'f', 'F'}:
        where['sex'] = sex.upper()

    result = table.find(**where)
    return list(result)


@app.route('/')
def index():
    "Get us started"
    return render_template('stack.html')


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
    return jsonify(name=name, sex=group, stats=stats)


@app.route('/<name>')
@app.route('/<name>/<sex>')
def name_stats(name, sex=None):
    "Get JSON stats for a single name"
    stats = get_name_stats(name, sex)
    return jsonify(name=name, sex=sex, stats=stats)


@app.template_global('s')
def static(filename):
    "Shortcut for static url"
    return url_for('static', filename=filename)


if __name__ == "__main__":
    app.run(debug=True)