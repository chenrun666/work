import json

import requests

from settings import *
# from update_cookie import cookie

data = {
    "flightWay": FLIGHTWAY,
    "classType": "ALL",
    "hasChild": HASBABY,
    "hasBaby": HASCHILD,
    "searchIndex": 1,
    "airportParams": [{
        "acity": CITYCODE[ENDLOCAL],  # code
        # "acityid": CODE[ENDLOCAL][1],  #
        "acityname": ENDLOCAL,  # 名字
        "date": STARTDATE,
        "dcity": CITYCODE[STARTLOCAL],
        # "dcityid": CODE[STARTLOCAL][1],
        "dcityname": STARTLOCAL
    }]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Content-Type": "application/json",
    "Cookie": """_abtest_userid=f390bd94-e557-489b-a366-e5ff6af81e26; _ga=GA1.2.2116162286.1543291365; _RSG=2SaEBib5Wo5g37P6IqJlE8; _RDG=2833e0a38effff2d2713d3aff39f83becd; _RGUID=5ca0165b-0b3a-4702-83af-4f44866470ea; DomesticUserHostCity=BJS|%b1%b1%be%a9; Union=SID=155952&AllianceID=4897&OUID=baidu81|index|||; Session=SmartLinkCode=U155952&SmartLinkKeyWord=&SmartLinkQuary=&SmartLinkHost=&SmartLinkLanguage=zh; gad_city=96617ee7af8aedd02bbece8583e0066e; _RF1=123.121.173.81; traceExt=campaign=CHNbaidu81&adid=index; _gid=GA1.2.1118693855.1548037898; MKT_Pagesource=PC; FD_SearchHistorty={"type":"S","data":"S%24%u4E0A%u6D77%28SHA%29%24SHA%242019-02-20%24%u6606%u660E%28KMG%29%24KMG%24%24%24"}; _bfa=1.1543291365458.gg8ic.1.1547455244969.1548037895125.3.13; _bfs=1.10; MKT_OrderClick=ASID=&CT=1548038692559&CURL=http%3A%2F%2Fflights.ctrip.com%2Fitinerary%2Foneway%2Fsha-kmg%3Fdate%3D2019-02-20&VAL={"pc_vid":"1543291365458.gg8ic"}; Mkt_UnionRecord=%5B%7B%22aid%22%3A%224897%22%2C%22timestamp%22%3A1548038692564%7D%5D; _jzqco=%7C%7C%7C%7C1548037898158%7C1.412384165.1543291366226.1548038608170.1548038692610.1548038608170.1548038692610.undefined.0.0.11.11; __zpspc=9.3.1548038596.1548038692.3%231%7Cbaidu%7Ccpc%7Cbaidu81%7C%25E6%2590%25BA%25E7%25A8%258B%25E5%25AE%2598%25E7%25BD%2591%25E9%25A6%2596%25E9%25A1%25B5%7C%23; _bfi=p1%3D10320673302%26p2%3D10320673302%26v1%3D13%26v2%3D12"""

}


def get_data(url):
    # 所有的航班信息
    all_flight = []
    result = requests.post(url, data=json.dumps(data), headers=headers).json()

    flight_list = result.get("data").get("routeList")
    for item in flight_list:
        flight = item.get("legs")[0].get("flight")
        all_flight.append(flight)

    return all_flight


if __name__ == '__main__':
    url = "http://flights.ctrip.com/itinerary/api/12808/products"
    all_flight = get_data(url)
    print(all_flight)
