import json
import requests



headers = {
    "Content-Type": "application/json"
}
data = {
    "header":
        {
            "carrier": "FD",
            "accountType": "4"
        },
    "params":
        {
            "purpose": "3"
        }
}


url = "192.168.1.174:9555/balanceScan/send?traceID=500"

result = requests.post(url, data=json.dumps(data), headers=headers)

print(result)
