from csv import reader
from urllib.request import urlopen
from codecs import iterdecode

from app.__init__ import app, db
from app.tables import Countries, Cases, Deaths, Recovered

rename = {
    "Antigua and Barbuda": "Antigua and Barb.",
    "Bosnia and Herzegovina": "Bosnia and Herz.",
    "Burma": "Myanmar",
    "Central African Republic": "Central African Rep.",
    "Congo (Brazzaville)": "Congo",
    "Congo (Kinshasa)": "Dem. Rep. Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Cyprus": "N. Cyprus",
    "Dominican Republic": "Dominican Rep.",
    "Equatorial Guinea": "Eq. Guinea",
    "Eswatini": "eSwatini",
    "Korea, South": "South Korea",
    "Saint Kitts and Nevis": "St. Kitts and Nevis",
    "Saint Vincent and the Grenadines": "St. Vin. and Gren.",
    "Sao Tome and Principe": "São Tomé and Principe",
    "South Sudan": "S. Sudan",
    "Taiwan*": "Taiwan",
    "North Macedonia": "Macedonia",
    "US": "United States of America",
    "Western Sahara": "W. Sahara"
}

pop_url = 'https://raw.githubusercontent.com/Xyresic/SoftDev/master/spring/18_d3/static/data/population.csv'
cases_url = 'https://data.humdata.org/hxlproxy/data/download/time_series_covid19_confirmed_global_narrow.csv?dest' \
            '=data_edit&filter01=merge&merge-url01=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
            '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
            '%3D1326629740%26single%3Dtrue%26output%3Dcsv&merge-keys01=%23country%2Bname&merge-tags01=%23country' \
            '%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode&filter02' \
            '=merge&merge-url02=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
            '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
            '%3D398158223%26single%3Dtrue%26output%3Dcsv&merge-keys02=%23adm1%2Bname&merge-tags02=%23country%2Bcode' \
            '%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode&merge-replace02=on' \
            '&merge-overwrite02=on&filter03=explode&explode-header-att03=date&explode-value-att03=value&filter04' \
            '=rename&rename-oldtag04=%23affected%2Bdate&rename-newtag04=%23date&rename-header04=Date&filter05=rename' \
            '&rename-oldtag05=%23affected%2Bvalue&rename-newtag05=%23affected%2Binfected%2Bvalue%2Bnum&rename' \
            '-header05=Value&filter06=clean&clean-date-tags06=%23date&filter07=sort&sort-tags07=%23date&sort' \
            '-reverse07=on&filter08=sort&sort-tags08=%23country%2Bname%2C%23adm1%2Bname&tagger-match-all=on&tagger' \
            '-default-tag=%23affected%2Blabel&tagger-01-header=province%2Fstate&tagger-01-tag=%23adm1%2Bname&tagger' \
            '-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03-header=lat&tagger-03-tag=%23geo' \
            '%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1&url=https%3A%2F%2Fraw' \
            '.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data' \
            '%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv '
deaths_url = 'https://data.humdata.org/hxlproxy/data/download/time_series_covid19_deaths_global_narrow.csv?dest' \
             '=data_edit&filter01=merge&merge-url01=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
             '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
             '%3D1326629740%26single%3Dtrue%26output%3Dcsv&merge-keys01=%23country%2Bname&merge-tags01=%23country' \
             '%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode&filter02' \
             '=merge&merge-url02=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
             '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
             '%3D398158223%26single%3Dtrue%26output%3Dcsv&merge-keys02=%23adm1%2Bname&merge-tags02=%23country%2Bcode' \
             '%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode&merge-replace02' \
             '=on&merge-overwrite02=on&filter03=explode&explode-header-att03=date&explode-value-att03=value&filter04' \
             '=rename&rename-oldtag04=%23affected%2Bdate&rename-newtag04=%23date&rename-header04=Date&filter05=rename' \
             '&rename-oldtag05=%23affected%2Bvalue&rename-newtag05=%23affected%2Binfected%2Bvalue%2Bnum&rename' \
             '-header05=Value&filter06=clean&clean-date-tags06=%23date&filter07=sort&sort-tags07=%23date&sort' \
             '-reverse07=on&filter08=sort&sort-tags08=%23country%2Bname%2C%23adm1%2Bname&tagger-match-all=on&tagger' \
             '-default-tag=%23affected%2Blabel&tagger-01-header=province%2Fstate&tagger-01-tag=%23adm1%2Bname&tagger' \
             '-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03-header=lat&tagger-03-tag=%23geo' \
             '%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1&url=https%3A%2F%2Fraw' \
             '.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data' \
             '%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv '
recovered_url = 'https://data.humdata.org/hxlproxy/data/download/time_series_covid19_recovered_global_narrow.csv?dest' \
                '=data_edit&filter01=merge&merge-url01=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
                '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
                '%3D1326629740%26single%3Dtrue%26output%3Dcsv&merge-keys01=%23country%2Bname&merge-tags01=%23country' \
                '%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode' \
                '&filter02=merge&merge-url02=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX' \
                '-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid' \
                '%3D398158223%26single%3Dtrue%26output%3Dcsv&merge-keys02=%23adm1%2Bname&merge-tags02=%23country' \
                '%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bsub%2Bcode%2C%23region%2Bintermediate%2Bcode&merge' \
                '-replace02=on&merge-overwrite02=on&filter03=explode&explode-header-att03=date&explode-value-att03' \
                '=value&filter04=rename&rename-oldtag04=%23affected%2Bdate&rename-newtag04=%23date&rename-header04' \
                '=Date&filter05=rename&rename-oldtag05=%23affected%2Bvalue&rename-newtag05=%23affected%2Binfected' \
                '%2Bvalue%2Bnum&rename-header05=Value&filter06=clean&clean-date-tags06=%23date&filter07=sort&sort' \
                '-tags07=%23date&sort-reverse07=on&filter08=sort&sort-tags08=%23country%2Bname%2C%23adm1%2Bname' \
                '&tagger-match-all=on&tagger-default-tag=%23affected%2Blabel&tagger-01-header=province%2Fstate&tagger' \
                '-01-tag=%23adm1%2Bname&tagger-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03' \
                '-header=lat&tagger-03-tag=%23geo%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1' \
                '&url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster' \
                '%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_recovered_global.csv '


def retrieve_reader(request):
    return reader(iterdecode(request, 'utf-8'))


def fill_db(file_reader, table):
    for row in file_reader:
        if row[2] == '0.0':
            continue
        name = rename[row[1]] if row[1] in rename else row[1]
        country = Countries.query.filter_by(name=name).first()
        if country is None:
            country = Countries.query.filter_by(code=row[6]).first()
            country.name = name
        case = Cases.query.filter_by(country_id=country.id, date=row[4]).first()
        if table is not Cases:
            entry = table.query.filter_by(cases_id=case.id, date=row[4]).first()
            if entry is None:
                entry = table(row[4], int(row[5]), country.id, case.id)
                db.session.add(entry)
            else:
                entry.amount += int(row[5])
        elif case is None:
            case = Cases(row[4], int(row[5]), country.id)
            db.session.add(case)
        else:
            case.amount += int(row[5])
    db.session.commit()


with app.app_context():
    db.drop_all()
    db.create_all()
    with urlopen(pop_url) as request:
        pop_reader = retrieve_reader(request)
        next(pop_reader)
        for line in pop_reader:
            country = Countries(line[1], int(line[2]))
            db.session.add(country)
    with urlopen(cases_url) as request:
        cases_reader = retrieve_reader(request)
        next(cases_reader)
        next(cases_reader)
        fill_db(cases_reader, Cases)
    with urlopen(deaths_url) as request:
        deaths_reader = retrieve_reader(request)
        next(deaths_reader)
        next(deaths_reader)
        fill_db(deaths_reader, Deaths)
    with urlopen(recovered_url) as request:
        recovered_reader = retrieve_reader(request)
        next(recovered_reader)
        next(recovered_reader)
        fill_db(recovered_reader, Recovered)
