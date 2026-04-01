import urllib.request
import json
import sys

client_id = "q8Y3EuiGXRYGjemuDFYv"
client_secret = "HLddlF0Qc1"

url = "https://openapi.naver.com/v1/datalab/search"
body_dict = {
    "startDate": "2025-03-01",
    "endDate": "2026-03-06",
    "timeUnit": "month",
    "keywordGroups": [
        {"groupName": "남양주백병원", "keywords": ["남양주백병원"]},
        {"groupName": "남양주정형외과", "keywords": ["남양주정형외과"]},
        {"groupName": "남양주신경과", "keywords": ["남양주신경과", "남양주 신경과"]}
    ]
}

body = json.dumps(body_dict)
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)
request.add_header("Content-Type", "application/json")

try:
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print(f"Error Code: {rescode}")
except Exception as e:
    print(f"Failed: {e}")
