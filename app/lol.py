import datetime
def main():
    a = datetime.datetime.today()
    numdays = 180
    dateList = []
    for x in range (0, numdays):
        date = a - datetime.timedelta(days = x)
        dateList.append(date.strftime('%Y-%m-%d'))

    print(dateList)

main()
