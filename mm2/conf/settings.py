# 测试环境
TEST = True
# 线上环境
# TEST = False

# 获取总价格失败，错误信息为'NoneType' object has no attribute 'group'
# 获取航班详细信息失败，错误信息是：list index out of range
TESTDATA = {'taskStatus': None, 'id': 1495762, 'taskType': 2, 'taskSource': 0, 'taskId': None, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_73c6709e234c4dc291c2fd7fc1111bed', 'orderNo': '369391145', 'depCity': 'KIX', 'arrCity': 'ICN', 'fromDate': '2019-01-30', 'retDate': None, 'flightNumber': 'MM011', 'tripType': 1, 'name': 'ZHOU/QIANG', 'email': '', 'accountType': '0', 'loginAccount': '', 'loginPassword': '', 'pnr': 'SDSGCE', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548691541000, 'createTime': 1548691211000}


# 获取总价格失败，错误信息为'NoneType' object has no attribute 'group'
# 获取航班详细信息失败，错误信息是：list index out of range
TESTDATA1 = {'taskStatus': None, 'id': 1495763, 'taskType': 2, 'taskSource': 0, 'taskId': None, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_e4404a2cc1ce4d66a33290144842b3aa', 'orderNo': '369397913', 'depCity': 'KIX', 'arrCity': 'HKG', 'fromDate': '2019-01-30', 'retDate': None, 'flightNumber': 'MM067', 'tripType': 1, 'name': 'LIN/YAOBIN', 'email': '', 'accountType': '0', 'loginAccount': '', 'loginPassword': '', 'pnr': '5CAQG6', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548691545000, 'createTime': 1548691211000}


# 获取乘客基本信息失败，错误信息：[Errno 22] Invalid argument
TESTDATA2 = {'taskStatus': None, 'id': 1504335, 'taskType': 2, 'taskSource': 1, 'taskId': 61612, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_93a714eddbea4e35962cfbbe248d50da', 'orderNo': '390036734', 'depCity': 'HKG', 'arrCity': 'KIX', 'fromDate': '2019-02-01', 'retDate': None, 'flightNumber': 'MM068', 'tripType': 1, 'name': 'KANG/JIAN', 'email': 'letaohangkong@163.com', 'accountType': '0', 'loginAccount': None, 'loginPassword': None, 'pnr': 'GA2Q5C', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548868364000, 'createTime': 1548868035000}


# 不同币种 HGK
TESTDATA3 = {'taskStatus': None, 'id': 1503234, 'taskType': 2, 'taskSource': 0, 'taskId': None, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_54ac76e13c3840419f89a2eda4d7d9b1', 'orderNo': '379751305', 'depCity': 'KIX', 'arrCity': 'HKG', 'fromDate': '2019-02-01', 'retDate': None, 'flightNumber': 'MM063', 'tripType': 1, 'name': 'HUANG/WEILIANG', 'email': '', 'accountType': '0', 'loginAccount': '', 'loginPassword': '', 'pnr': 'Z4XCP8', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548865688000, 'createTime': 1548864019000}
# 人民币
TESTDATA4 = {'taskStatus': None, 'id': 1503234, 'taskType': 2, 'taskSource': 0, 'taskId': None, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_54ac76e13c3840419f89a2eda4d7d9b1', 'orderNo': '379751305', 'depCity': 'KIX', 'arrCity': 'HKG', 'fromDate': '2019-02-01', 'retDate': None, 'flightNumber': 'MM063', 'tripType': 1, 'name': 'NGUYEN/THITRANG', 'email': '', 'accountType': '0', 'loginAccount': '', 'loginPassword': '', 'pnr': 'ASABQH', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548865688000, 'createTime': 1548864019000}



# error
TESTDATA5 = {'taskStatus': None, 'id': 1505033, 'taskType': 1, 'taskSource': 1, 'taskId': 69558, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_3683d650ba554bf3a5aa5f7c75489ecd', 'orderNo': '392322867', 'depCity': 'HND', 'arrCity': 'PVG', 'fromDate': '2019-02-04', 'retDate': None, 'flightNumber': 'MM899', 'tripType': 1, 'name': 'KANG/JIAN', 'email': 'letaohangkong@163.com', 'accountType': '0', 'loginAccount': None, 'loginPassword': None, 'pnr': 'GA2Q5C', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548914014000, 'createTime': 1548914014000}


