import datetime

def date_formatter(string):
    dmap = {
        "января":1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }
    string = string.split(" ")
    if "вчера" in string:
        return datetime.date(year=(datetime.datetime.now() - datetime.timedelta(days=1)).year,
                             month=(datetime.datetime.now() - datetime.timedelta(days=1)).month,
                             day=(datetime.datetime.now() - datetime.timedelta(days=1)).day)
    elif "в" in string:
        for i in string:
            if i in dmap:
                return datetime.date(year=2022,month=dmap[i],day=int(string[0]))
    else:
        return datetime.date.today()