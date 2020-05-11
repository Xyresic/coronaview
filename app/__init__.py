import os, sys, csv
from flask import Flask, render_template, jsonify
from tables import db, Countries, Cases, Deaths, Recovered, Company, Sector, DailyData
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
    url = 'https://pkgstore.datahub.io/core/s-and-p-500-companies-financials/constituents-financials_json/data/ddf1c04b0ad45e44f976c1f32774ed9a/constituents-financials_json.json?fbclid=IwAR03-dtqPvXAiITWjGLAuWN_qLK2aYd0Lhhk_Q5lMKh3cIUVW-KfgNwa4Fs'
    url_company_1 = "https://financialmodelingprep.com/api/v3/historical-price-full/"
    url_company_2 = "?serietype=line"
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
    end = len(data)
    set_of_sectors = set()
    #handles S&P 500 Index data
    S_P = Company('S&P 500','None','None',0)
    url_SP = 'https://financialmodelingprep.com/api/v3/historical-price-full/index/%5EGSPC'
    req_SP = urllib.Request(url_SP, headers=hdr)
    data_SP = json.loads(urllib.urlopen(req_SP).read())['historical']
    for j in range(0,365):
        daily_data = DailyData(data_SP[j]['date'],data_SP[j]['close'])
        S_P.data_points.append(daily_data)
        db.session.add(daily_data)
    #going through all the companies in S&P 500 while putting them in sectors and getting their daily data over a year
    while (i < end):
        sector = None
        #create company
        company = Company(data[i]['Name'],data[i]['Sector'],data[i]['Symbol'],data[i]['Market Cap'])
        #create a sector or add the compnay to a sector
        if data[i]['Sector'] not in set_of_sectors:
            set_of_sectors.add(data[i]['Sector'])
            sector = Sector(data[i]['Sector'])
            sector.companies.append(company)
        else:
            sector = Sector.query.filter_by(name = data[i]['Sector']).first()
            sector.companies.append(company)
        #get historical data on that company
        req_company = urllib.Request(url_company_1 + data[i]['Symbol'] + url_company_2, headers=hdr)
        data_company = json.loads(urllib.urlopen(req_company).read())
        data_company = data_company['historical'][len(data_company['historical'])-365:len(data_company['historical'])]
        for j in range(0,365):
            daily_data = DailyData(data_company[j]['date'],data_company[j]['close'])
            company.data_points.append(daily_data)
            db.session.add(daily_data)
        db.session.add(sector)
        db.session.add(company)
        i += 1
    db.session.add(S_P)
    db.session.commit()

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


@app.route('/data/economy')
def economy():
    return "insert economy data here"


if __name__ == '__main__':
    app.debug = True
    app.run()
