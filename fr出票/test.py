import json

with open("./test.json", "r") as f:
    test_data = json.load(f)


print(test_data["data"]["passengerVOList"])

print(test_data["data"]["depAirport"])

print(test_data["data"]["targetPrice"])



# ,
#       {
#         "sex": "F",
#         "cardNum": "G78979834",
#         "baggageWeight": 20,
#         "id": 116594,
#         "baggageWeightStr": null,
#         "nationality": "CN",
#         "birthday": "2016-10-01",
#         "name": "CHEN/RUN",
#         "cardExpired": "20261103",
#         "cardIssuePlace": "CN",
#         "payTaskId": null
#       },
#       {
#         "sex": "F",
#         "cardNum": "G78979834",
#         "baggageWeight": 50,
#         "id": 116594,
#         "baggageWeightStr": null,
#         "nationality": "CN",
#         "birthday": "2016-10-01",
#         "name": "PENG/HUIXIAN",
#         "cardExpired": "20261103",
#         "cardIssuePlace": "CN",
#         "payTaskId": null
#       },
#       {
#         "sex": "F",
#         "cardNum": "G78979834",
#         "baggageWeight": 50,
#         "id": 116594,
#         "baggageWeightStr": null,
#         "nationality": "CN",
#         "birthday": "2016-10-01",
#         "name": "WANG/SHUAIDONG",
#         "cardExpired": "20261103",
#       "cardIssuePlace": "CN",
#       "payTaskId": null
#       },
#       {
#         "sex": "F",
#         "cardNum": "G78979834",
#         "baggageWeight": 50,
#         "id": 116594,
#         "baggageWeightStr": null,
#         "nationality": "CN",
#         "birthday": "2016-10-01",
#         "name": "GAO/XIAOQIANG",
#         "cardExpired": "20261103",
#       "cardIssuePlace": "CN",
#       "payTaskId": null
#       },
#       {
#         "sex": "F",
#         "cardNum": "G78979834",
#         "baggageWeight": 50,
#         "id": 116594,
#         "baggageWeightStr": null,
#         "nationality": "CN",
#         "birthday": "1990-10-01",
#         "name": "CHEN/JING",
#         "cardExpired": "20261103",
#       "cardIssuePlace": "CN",
#       "payTaskId": null
#       }