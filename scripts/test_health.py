import time
import requests

url = 'http://127.0.0.1:8000/health'
for i in range(12):
    try:
        r = requests.get(url, timeout=3)
        print('STATUS', r.status_code)
        print(r.text)
        break
    except Exception as e:
        print('wait...', i, str(e))
        time.sleep(2)
else:
    print('timeout, server not responding')
