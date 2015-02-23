"""
Flask app serving up random names for no good reason
"""
import os
import dataset
from flask import Flask, g, render_template, jsonify
from redis import StrictRedis

# using this for prototyping
DATABASE_URL = "sqlite:///names.db"
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

app = Flask(__name__)
app.config.from_object(__name__)

redis = StrictRedis.from_url(REDIS_URL)
db = dataset.connect(DATABASE_URL)

@app.route('/')
def index():
    "Get us started"
    return render_template('index.html')


@app.route('/name')
@app.route('/name/<group>')
def get_random_name(group=None):
    "Get a random name"
    if group in ('f', 'm', 'all'):
        key = "names:{}".format(group)
    else:
        key = "names:all"

    return redis.srandmember(key)


def name_stats(name, sex=None):
    "Get stats for a single name"
    table = db['names']
    where = {'name': name}
    if sex:
        where['sex'] = sex

    result = table.find(**where)
    return list(result)


if __name__ == "__main__":
    app.run(debug=True)