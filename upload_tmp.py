import requests
import sys

file_path = r"C:\Users\USER\.gemini\antigravity\brain\5eae929f-1c4c-4c80-ab27-6119aa6f3429\warm_doctor_care_1773913004797.png"

try:
    with open(file_path, "rb") as f:
        url = "https://catbox.moe/user/api.php"
        files = {'fileToUpload': f}
        data = {'reqtype': 'fileupload'}
        r = requests.post(url, files=files, data=data)
        print("URL:", r.text)
except Exception as e:
    print("Error:", e)
