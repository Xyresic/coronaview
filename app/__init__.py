import os, sys, csv
from flask import Flask, render_template, jsonify
from tables import db

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./static/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

db.init_app(app)


def get_data():
    parse = {}
    populations = {}
    with open('./app/static/data/population.csv','r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            populations[row[1]] = int(row[2])
    with open('./app/static/data/covid19_confirmed.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        next(reader)
        for row in reader:
            date = row[4]
            if date not in list(parse):
                parse[date] = {}
            if row[6] == '':
                continue
            name = rename[row[1]] if row[1] in list(rename) else row[1]
            if row[1] == 'France':
                pop = populations['FRA']
            elif row[1] == 'Netherlands':
                pop = populations['NLD']
            elif row[1] == 'United Kingdom':
                pop = populations['GBR']
            elif row[1] == 'Canada':
                pop = populations['CAN']
            else:
                pop = populations[row[6]]
            if name in list(parse[date]):
                parse[date][name][0] = int(parse[date][name][0]*pop+int(row[5]))/pop
                parse[date][name][1] += int(row[5])
            else:
                parse[date][name] = [int(row[5])/pop, int(row[5])]
    return parse


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


@app.route('/data')
def infections():
    return jsonify(get_data())


if __name__ == '__main__':
    app.debug = True
    app.run()
