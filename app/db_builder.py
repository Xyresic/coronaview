from __init__ import app, db
from tables import Countries, Cases, Deaths, Recovered, Company, Sector, DailyData
from csv import reader
from urllib.request import urlopen
from codecs import iterdecode
import urllib.request as urllib
import json

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

pop_url = 'https://raw.githubusercontent.com/Xyresic/SoftDev/master/18_d3/static/data/population.csv'
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

with app.app_context():
    dates = ['2020-05-13', '2020-05-11', '2020-05-09', '2020-05-07', '2020-05-05', '2020-05-03', '2020-05-01', '2020-04-29', '2020-04-27', '2020-04-25',
'2020-04-23', '2020-04-21', '2020-04-19', '2020-04-17', '2020-04-15', '2020-04-13', '2020-04-11', '2020-04-09', '2020-04-07', '2020-04-05', '2020-04-03', '2020-04-01', '2020-03-30', '2020-03-28', '2020-03-26', '2020-03-24', '2020-03-22', '2020-03-20', '2020-03-18', '2020-03-16', '2020-03-14', '2020-03-12', '2020-03-10', '2020-03-08', '2020-03-06', '2020-03-04', '2020-03-02', '2020-02-29', '2020-02-27',
'2020-02-25', '2020-02-23', '2020-02-21', '2020-02-19', '2020-02-17', '2020-02-15', '2020-02-13', '2020-02-11', '2020-02-09', '2020-02-07', '2020-02-05',
'2020-02-03', '2020-02-01', '2020-01-30', '2020-01-28', '2020-01-26', '2020-01-24', '2020-01-22', '2020-01-20', '2020-01-18', '2020-01-16',
'2020-01-14', '2020-01-12', '2020-01-10', '2020-01-08', '2020-01-06', '2020-01-04', '2020-01-02', '2019-12-31', '2019-12-29', '2019-12-27',
'2019-12-25', '2019-12-23', '2019-12-21', '2019-12-19', '2019-12-17', '2019-12-15', '2019-12-13', '2019-12-11', '2019-12-09', '2019-12-07', '2019-12-05', '2019-12-03', '2019-12-01', '2019-11-29', '2019-11-27', '2019-11-25', '2019-11-23', '2019-11-21', '2019-11-19', '2019-11-17']

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
        if len(data_company) > 0:
            print(data_company['symbol'])
            parsed_data_company = []
            b = 1
            skip = False
            for date in dates:
                while date != data_company['historical'][len(data_company['historical'])-b]['date']:
                    b+=1
                    if len(data_company['historical'])-b == 0:
                        b = 1
                        skip = True
                        break
                if skip:
                    skip = False
                    continue
                else:
                    parsed_data_company.append(data_company['historical'][len(data_company['historical'])-b])
            # data_company = data_company['historical'][len(data_company['historical'])-365:len(data_company['historical'])]
            if len(parsed_data_company) > 0:
                print(parsed_data_company[0]['date'])
                for j in range(0,len(parsed_data_company)):
                    daily_data = DailyData(parsed_data_company[j]['date'],parsed_data_company[j]['close'])
                    company.data_points.append(daily_data)
                    db.session.add(daily_data)
        db.session.add(sector)
        db.session.add(company)
        i += 1
    db.session.add(S_P)
    db.session.commit()
