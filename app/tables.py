from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.String(3), nullable=False)
    population = db.Column(db.Integer)

    cases = db.relationship('Cases', backref='country', lazy='dynamic')
    deaths = db.relationship('Deaths', backref='country', lazy='dynamic')
    recovered = db.relationship('Recovered', backref='country', lazy='dynamic')

    def __init__(self, code, population):
        self.code = code
        self.population = population


class Cases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    country_id = db.Column(db.ForeignKey('countries.id'))

    deaths = db.relationship('Deaths', backref='cases', uselist=False)
    recovered = db.relationship('Recovered', backref='cases', uselist=False)

    def __init__(self, date, amount, country_id):
        self.date = date
        self.amount = amount
        self.country_id = country_id


class Deaths(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    country_id = db.Column(db.ForeignKey('countries.id'))
    cases_id = db.Column(db.ForeignKey('cases.id'))

    def __init__(self, date, amount, country_id, cases_id):
        self.date = date
        self.amount = amount
        self.country_id = country_id
        self.cases_id = cases_id


class Recovered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    country_id = db.Column(db.ForeignKey('countries.id'))
    cases_id = db.Column(db.ForeignKey('cases.id'))

    def __init__(self, date, amount, country_id, cases_id):
        self.date = date
        self.amount = amount
        self.country_id = country_id
        self.cases_id = cases_id