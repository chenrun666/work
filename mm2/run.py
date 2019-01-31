import json
import uuid
import time

import requests

from bin.check import AirMM
from bin.log import logger
from conf.settings import *
from bin.get_task import *

if __name__ == '__main__':
    back_fill_url = "http://47.92.39.84:9444/resultTask?traceID=" + str(uuid.uuid4())
    interface_url = "http://47.92.39.84:9444/sendTasks?carrier=MM&traceID=065de17a-fafb-11e8-8eb2-f2801f1b9fd1"

    if TEST:
        # 测试环境

        check_data = AirMM({})
        result = check_data()
        print(json.dumps(result))

    else:
        # 线上环境
        # 获取任务
        while 1:
            response = get_response()  # 获取任务
            if response:
                logger.info(f"获取到任务|{response[0]}")
                check_data = AirMM(response[0])
                try:
                    result = check_data()
                except Exception as e:
                    msg = f"未知错误, {str(e)}"
                    check_data.response["msg"] = msg
                    result = check_data.response
                    logger.error(msg)

                try:
                    back_fill_back = requests.post(url=back_fill_url, data=json.dumps(result),
                                                   headers={"content-type": "application/json"})
                    logger.info("回填状态 -> " + back_fill_back.text)
                except Exception as e:
                    logger.error("回填出错 ->" + str(e))

            else:
                logger.info("没有获取到任务，等待N秒")
                time.sleep(10)

