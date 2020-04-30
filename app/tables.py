from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(3))
    population = db.Column(db.Integer)

    cases = db.relationship('Cases', backref='country')
    deaths = db.relationship('Deaths', backref='country')
    recovered = db.relationship('Recovered', backref='country')

    def __init__(self, name, code, population):
        self.name = name
        self.code = code
        self.population = population


class Cases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
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
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    country_id = db.ForeignKey('countries.id')
    cases_id = db.Column(db.ForeignKey('cases.id'))

    def __init__(self, date, amount, country_id, cases_id):
        self.date = date
        self.amount = amount
        self.country_id = country_id
        self.cases_id = cases_id


class Recovered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    country_id = db.ForeignKey('countries.id')
    cases_id = db.Column(db.ForeignKey('cases.id'))

    def __init__(self, date, amount, country_id, cases_id):
        self.date = date
        self.amount = amount
        self.country_id = country_id
        self.cases_id = cases_id