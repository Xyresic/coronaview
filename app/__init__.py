import os, sys, csv
from flask import Flask, render_template, jsonify, request
from tables import db, Countries, Cases, Deaths, Recovered, Economy

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

db.init_app(app)


def get_data(table):
    data = {}
    for entry in table.query.all():
        date = entry.date
        country = entry.country
        if date not in data:
            data[date] = {}
        data[date][country.name] = [entry.amount / country.population, entry.amount]
    return data


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.form.get('Employment Impact') == 'Employment Impact':
        return render_template('index2.html')
    elif request.form.get('World Cases') == 'World Cases':
        return render_template("index.html")
    return render_template('index.html')

@app.route('/data/<country>/<date>')
def data(country, date):
    entry = Countries.query.filter_by(name=country).first()

    def find(query):
        return query.filter_by(date=date).first().amount

    json = {'population': entry.population,
            'cases': find(entry.cases),
            'deaths': find(entry.deaths),
            'recoveries': find(entry.recovered)}
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

@app.route('/data/economy')
def economy():
    return "insert economy data here"
    # return jsonify(get_data(Economy))

if __name__ == '__main__':
    app.debug = True
    app.run()
