import os
import sys
import time

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)

from lib.init_browser import OpenBrowser

if __name__ == '__main__':
    with OpenBrowser() as driver:
        time.sleep(4)





