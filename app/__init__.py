import os

from flask import Flask, render_template, jsonify
from rq import Queue
from app.worker import conn

from app.tables import db, Countries, Cases, Deaths, Recovered

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# start database
db.init_app(app)


def get_data(table):
    data = {}
    if table == Cases:
        for entry in table.query.all():
            date = entry.date
            country = entry.country
            if date not in data:
                data[date] = {}
            data[date][country.name] = [entry.amount / country.population, entry.amount]
    else:
        for entry in table.query.all():
            date = entry.date
            country = entry.country
            if date not in data:
                data[date] = {}
            cases = entry.cases.amount
            data[date][country.name] = [0 if cases == 0 else (entry.amount / cases), entry.amount]
    return data

#start background jobs
with app.app_context():
    q = Queue(connection=conn)
    cases = q.enqueue(jsonify, get_data(Cases))
    deaths = q.enqueue(jsonify, get_data(Deaths))
    recoveries = q.enqueue(jsonify, get_data(Recovered))

@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


@app.route('/data/<country>')
def data(country):
    entry = Countries.query.filter_by(name=country).first()
    json = {'population': entry.population,
            'cases': [case.amount for case in entry.cases.all()][::-1],
            'deaths': [case.amount for case in entry.deaths.all()][::-1],
            'recoveries': [case.amount for case in entry.recovered.all()][::-1]}
    return jsonify(json)


@app.route('/data/cases')
def cases():
    return cases


@app.route('/data/deaths')
def deaths():
    return deaths


@app.route('/data/recoveries')
def recoveries():
    return recoveries


if __name__ == '__main__':
    app.debug = True
    app.run()
