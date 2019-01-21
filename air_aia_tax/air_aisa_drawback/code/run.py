import logging
import time, json
from drawback_auto_client import do_login, get_order, drawback, init_driver, check_result, call_back_task

logger = logging.getLogger("__name__")

if __name__ == '__main__':

    with open('config.json', "r", encoding="GBK") as f:
        config = json.loads(f.read())
    while True:
        # order = get_order(config, type="real")
        order = get_order(config)
        if order:
            driver = init_driver()
            data = drawback(driver, order, config)
            # data = check_result(driver,order)
            call_back_task(config, data)
            driver.close()
            break
        else:
            logger.info("没有取到订单信息")
