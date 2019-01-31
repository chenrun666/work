"""
获取任务
"""
import json

import requests

from bin.log import logger
from conf.settings import *


def get_task():
    taskheaders = {'Content-Type': 'application/json'}
    data = {
        "clientType": CLIENTTYPE,
        "machineCode": MACHINECODE
    }
    taskJson = requests.post("http://47.92.119.88:18002/getBookingPayTask",
                             data=json.dumps(data), headers=taskheaders)
    return taskJson.text


def back_fill(data):
    taskheaders = {'Content-Type': 'application/json'}
    url = 'http://47.92.119.88:18002/bookingPayTaskResult'
    response = requests.post(url, data=json.dumps(data), headers=taskheaders)
    if json.loads(response.text)["status"] == 'Y':
        logger.info('回填任务成功')
        with open('../logs/success_data.txt', 'a+')as f:
            f.write(json.dumps(data) + '\n')
        return True
    else:
        logger.info('回传任务失败')
        with open('../logs/error_data.txt', 'a+')as f:
            f.write(json.dumps(data) + '\n')
        return False

