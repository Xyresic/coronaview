import os
from flask import Flask, render_template, jsonify
from tables import db, Countries, Cases, Deaths, Recovered, Company, DailyData, Sector

import urllib.request as urllib
import json

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# start database
db.init_app(app)


# printing companies data to confirm successful data parse
# with app.app_context():
#     companies = Company.query.all()
#     for company in companies:
#         if len(company.data_points) > 0:
#             print(company.data_points[0].date)
#     sector = Sector.query.filter_by(name = 'Industrials').first()
#     for data in sector.data_points:
#         print(data.date)


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


def get_sector_data(sector_name):
    sector = Sector.query.filter_by(name=sector_name).first()
    data_points = sector.data_points
    data = {}
    data['points'] = []
    for point in data_points:
        sub_data = {}
        sub_data['date'] = point.date
        sub_data['price'] = point.price
        data['points'].append(sub_data)
    return data


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


@app.route('/econ/<sector_name>', methods=['GET', 'POST'])
def econ(sector_name):
    if sector_name == 'Industrials' or sector_name == 'Financials':
        sector_name = sector_name[:-1]
    return render_template('econ.html', sector_name=sector_name)


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


@app.route('/data/sector/<sector_name>')
def sectors(sector_name):
    return jsonify(get_sector_data(sector_name))


if __name__ == '__main__':
    app.debug = True
    app.run()
