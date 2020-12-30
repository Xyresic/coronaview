import os

from flask import Flask, render_template, jsonify

from app.tables import db, Countries, Cases, Deaths, Recovered

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# start database
db.init_app(app)


def get_data(table, date):
    data = {}
    for entry in table.query.filter_by(date=date).all():
        country = entry.country
        if table == Cases:
            data[country.name] = [entry.amount / country.population, entry.amount]
        else:
            cases = entry.cases.amount
            data[country.name] = [0 if cases == 0 else (entry.amount / cases), entry.amount]
    return data


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html', range=len(Cases.query.filter_by(country_id=2).all()))


@app.route('/data/<country>')
def data(country):
    entry = Countries.query.filter_by(name=country).first()
    json = {'population': entry.population,
            'cases': [case.amount for case in entry.cases.all()][::-1],
            'deaths': [case.amount for case in entry.deaths.all()][::-1],
            'recoveries': [case.amount for case in entry.recovered.all()][::-1]}
    return jsonify(json)


@app.route('/data/cases/<date>')
def cases(date):
    return jsonify(get_data(Cases, date))


@app.route('/data/deaths/<date>')
def deaths(date):
    return jsonify(get_data(Deaths, date))


@app.route('/data/recoveries/<date>')
def recoveries(date):
    return jsonify(get_data(Recovered, date))


if __name__ == '__main__':
    app.run()
