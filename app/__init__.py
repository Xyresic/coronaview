import os
from flask import Flask, render_template, jsonify

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
    return jsonify(get_data(Cases))


@app.route('/data/deaths')
def deaths():
    return jsonify(get_data(Deaths))


@app.route('/data/recoveries')
def recoveries():
    return jsonify(get_data(Recovered))


if __name__ == '__main__':
    app.debug = True
    app.run()
