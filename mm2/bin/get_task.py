import time
import uuid

import requests
from bin.log import logger

back_fill_url = "http://47.92.39.84:9444/resultTask?traceID=" + str(uuid.uuid4())
interface_url = "http://47.92.39.84:9444/sendTasks?carrier=MM&traceID=065de17a-fafb-11e8-8eb2-f2801f1b9fd1"


def get_response():
    try:
        response = requests.get(interface_url).json().get("data")
        return response
    except Exception as e:
        logger.error(f"获取任务失败, 错误信息是：{str(e)}")
        logger.info("获取任务失败，等待30秒，重新获取")
        time.sleep(30)
        get_response()



