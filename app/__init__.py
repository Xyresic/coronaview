import os, sys, csv
from flask import Flask, render_template, jsonify
from tables import db, Countries, Cases, Deaths, Recovered
import urllib.request as urllib
import json

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# start database
db.init_app(app)

with app.app_context():
    db.create_all()
    url = "https://pkgstore.datahub.io/core/s-and-p-500-companies-financials/constituents-financials_json/data/ddf1c04b0ad45e44f976c1f32774ed9a/constituents-financials_json.json?fbclid=IwAR03-dtqPvXAiITWjGLAuWN_qLK2aYd0Lhhk_Q5lMKh3cIUVW-KfgNwa4Fs" + str(x)
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }
    req = urllib.Request(url, headers=hdr)
    data = json.loads(urllib.urlopen(req).read())
    i = 0
    end = 500
    S_P = {}
    while (i < end):
        company = Company(data[i]['Name'],data[i]['Sector'],data[i]['Price'],data[i]['Market Cap'])
        db.session.add(company)
        i += 1
    db.session.commit()

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


if __name__ == '__main__':
    app.debug = True
    app.run()
