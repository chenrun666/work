import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
}

url = "http://www.ctrip.com/"
index = requests.get(url, headers=headers)
if index.status_code == 200:
    cookie = index.cookies
    print(cookie)
    print("成功获取首页cookie值")


if __name__ == '__main__':
    url = "http://www.ctrip.com/"
    index = requests.get(url, headers=headers)
    cookie = index.cookies
    set_cookie = index.headers.get("Set-Cookie")




