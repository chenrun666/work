import requests, random, json, re, time

user_agent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
]


# 从网站获取json数据
def get_data(adult, teen, chirld, date, Destination, orgin):
    url0 = 'https://desktopapps.ryanair.com/v4/en-us/availability?' \
           'ADT={}&CHD={}&DateOut={}&Destination={}' \
           '&FlexDaysOut=4&INF=0&IncludeConnectingFlights=true' \
           '&Origin={}' \
           '&RoundTrip=false&TEEN=0&ToUs=AGREED&exists=false' \
           '&promoCode=' \
        .format(adult, chirld, date, Destination, orgin)

    data = requests.get(url0, headers={"User-Agent": random.choice(user_agent)},
                        verify=False, timeout=None)
    return [data.text, date]


# 解析函数,拿到仓位码
def parse_data(datas):
    # print(datas)
    dicts = {}
    # dicts["promoStatus"] = task_response["promoStatus"]
    if "No HTTP resource was found that matches the request URI." in datas:
        # if data["message"] == "No HTTP resource was found that matches the request URI.":
        msg = "出现  No HTTP resource was found that matches the request URI"
        routings = []
        dicts["routings"] = routings
        return dicts
    try:
        data = json.loads(datas[0])
    except:
        msg = "未能解析返回的数据，记录重试"
        routings = []
        dicts["routings"] = routings
        return dicts
    routings = []
    dates = data["trips"][0]["dates"]
    t = datas[1]
    for date in dates:
        dateOut = date["dateOut"]
        if t in dateOut:
            flights = date["flights"]
            if flights != []:
                for f in flights:
                    flightKey = f["flightKey"]
                    fromSegments = []
                    routingss = {}
                    try:
                        # 仓位信息
                        fareKey = f["regularFare"]["fareKey"]
                        if len(fareKey) < 4:
                            fareKey = fareKey[0]
                        # 价格信息
                    except:
                        routings = []
                        msg = "此日期航班已经售完"
                        print(msg)
                        dicts["routings"] = routings
                        return dicts
                    for se in f["segments"]:
                        fromSegmentss = {}
                        fromSegmentss["cabin"] = fareKey
                        fromSegmentss["flightKey"] = flightKey
                        fromSegments.append(fromSegmentss)
                    routingss["fromSegments"] = fromSegments
                    routings.append(routingss)
                    dicts["routings"] = routings
                return dicts
            else:
                msg = "此日期没有航班,"
                routings = []
                dicts["routings"] = routings
                return dicts
