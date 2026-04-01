import subprocess
import time
import os
import urllib.request
import urllib.error

print("Killing chrome...")
os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
time.sleep(3)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = r"C:\Users\USER\AppData\Local\Google\Chrome\User Data"

print("Launching chrome via subprocess...")
subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9222",
    f"--user-data-dir={user_data_dir}",
    "--profile-directory=Default",
    "--no-first-run",
    "--restore-last-session=false"
])

print("Waiting 4 seconds for CDP port to open...")
time.sleep(4)

print("Checking port 9222 on 127.0.0.1...")
try:
    req = urllib.request.Request("http://127.0.0.1:9222/json/version")
    response = urllib.request.urlopen(req, timeout=3).read().decode()
    print("✅ SUCCESS:", response[:200])
except urllib.error.URLError as e:
    print("❌ FAILED:", e)
except Exception as e:
    print("❌ FAILED (Other):", e)
